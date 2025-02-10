import openpyxl

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db.models.functions import Concat
from django.forms import BaseInlineFormSet
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.html import format_html

from jalali_date import datetime2jalali, date2jalali
from jalali_date.admin import ModelAdminJalaliMixin

from .models import Session, JudgeAssignment
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, F, Case, When, Value, CharField
from django import forms
from jalali_date.widgets import AdminJalaliDateWidget
from django_flatpickr.widgets import TimePickerInput  # Import Flatpickr widget

from schedule.models import Schedule

from university_adminstration.models import FacultyEducationalGroup, Student


class MonthFilter_created_at(admin.SimpleListFilter):
    title = _('بر اساس زمان ایجاد شده ')
    parameter_name = 'month_created_at'

    def lookups(self, request, model_admin):
        return (
            ('1', _('فروردین')),
            ('2', _('اردیبهشت')),
            ('3', _('خرداد')),
            ('4', _('تیر')),
            ('5', _('مرداد')),
            ('6', _('شهریور')),
            ('7', _('مهر')),
            ('8', _('آبان')),
            ('9', _('آذر')),
            ('10', _('دی')),
            ('11', _('بهمن')),
            ('12', _('اسفند')),
        )

    def queryset(self, request, queryset):
        if self.value():
            try:
                jalali_month = int(self.value())  # Convert string to integer
            except ValueError:
                return queryset  # If invalid input, return unfiltered queryset

            # Get only required fields from DB (optimization)
            created_at_dates = queryset.values_list('id', 'created_at')

            # Filter using datetime2jalali without looping over queryset directly
            matching_ids = [
                id for id, created_at in created_at_dates
                if created_at and datetime2jalali(created_at).month == jalali_month
            ]

            return queryset.filter(id__in=matching_ids)  # Filter efficiently

        return queryset  # If no filter is applied, return the original queryset


class MonthFilter_updated_at(admin.SimpleListFilter):
    title = _('بر اساس زمان ویرایش شده')
    parameter_name = 'month_updated_at'

    def lookups(self, request, model_admin):
        return (
            ('1', _('فروردین')),
            ('2', _('اردیبهشت')),
            ('3', _('خرداد')),
            ('4', _('تیر')),
            ('5', _('مرداد')),
            ('6', _('شهریور')),
            ('7', _('مهر')),
            ('8', _('آبان')),
            ('9', _('آذر')),
            ('10', _('دی')),
            ('11', _('بهمن')),
            ('12', _('اسفند')),
        )

    def queryset(self, request, queryset):
        if self.value():
            try:
                jalali_month = int(self.value())  # Convert string to integer
            except ValueError:
                return queryset  # If invalid input, return unfiltered queryset

            # Get only required fields from DB (optimization)
            updated_at_dates = queryset.values_list('id', 'updated_at')

            # Filter using datetime2jalali without looping over queryset directly
            matching_ids = [
                id for id, updated_at in updated_at_dates
                if updated_at and datetime2jalali(updated_at).month == jalali_month
            ]

            return queryset.filter(id__in=matching_ids)  # Filter efficiently

        return queryset  # If no filter is applied, return the original queryset


class SupervisorCountFilter(admin.SimpleListFilter):
    title = _('تعداد استاد راهنما')
    parameter_name = 'supervisor_count'

    def lookups(self, request, model_admin):
        return [
            ('1', _('یک استاد راهنما')),
            ('2', _('دو استاد راهنما')),
        ]

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(
                supervisor1__isnull=False,
                supervisor2__isnull=True,
            )
        elif self.value() == '2':
            return queryset.filter(
                supervisor1__isnull=False,
                supervisor2__isnull=False,
            )
        return queryset


class Consultant_ProfessorCountFilter(admin.SimpleListFilter):
    title = _('تعداد استاد مشاور')
    parameter_name = 'Consultant_Professor_count'

    def lookups(self, request, model_admin):
        return [
            ('0', _('بدون استاد مشاور')),
            ('1', _('یک استاد مشاور')),
            ('2', _('دو استاد مشاور')),
        ]

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(
                supervisor3__isnull=True,
                supervisor4__isnull=True,
            )
        elif self.value() == '1':
            return queryset.filter(
                Q(supervisor3__isnull=True,
                  supervisor4__isnull=False, ) |
                Q(supervisor3__isnull=False,
                  supervisor4__isnull=True, )
            )
        elif self.value() == '2':
            return queryset.filter(
                supervisor3__isnull=False,
                supervisor4__isnull=False,
            )
        return queryset


class JudgeAssignmentForm(forms.ModelForm):
    class Meta:
        model = JudgeAssignment
        fields = ['judge']


class JudgeAssignmentFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()

        # Judges will be accessible here if you need to validate only within the inline formset
        judges = [
            form.cleaned_data.get('judge')
            for form in self.forms
            if not form.cleaned_data.get('DELETE', False)  # Exclude deleted judges
        ]

        self.validate_judges(judges)

        self.validate_judges_as_professors_db(judges)

        self.validate_not_duplicate_judges_at_sameSession(judges)

        self.validate_not_duplicate_professors_and_judges_atSameSession(judges)

        self.validate_professors_as_judges_db()

    def validate_judges(self, judges):
        session = self.instance
        # === check None Fields ! ===
        found_error = False
        errors = []
        if session.schedule_id == None:
            found_error = True
            errors.append("❌مقدار زمانبندی لازم است")
        if session.date == None:
            found_error = True
            errors.append("❌مقدار تاریخ لازم است")
        if session.start_time == None:
            found_error = True
            errors.append("❌مقدار ساعت شروع لازم است")
        if session.end_time == None:
            errors.append("❌مقدار زمان پایان لازم است")
        if session.student_id == None:
            found_error = True
            errors.append("❌مقدار دانشجو لازم است")
        if session.supervisor1_id == None:
            found_error = True
            errors.append("❌مقدار استاد مشاور اول لازم است")
        if session.graduate_monitor_id == None:
            found_error = True
            errors.append("❌مقدار ناظر تحصیلات تکمیلی لازم است")
        if session.class_number == None:
            found_error = True
            errors.append("❌لطفا شماره کلاس را انتخاب کنید")

        if found_error:
            messages.error(self.request, " | ".join(errors))
            raise ValidationError(
                f''
            )
        # Find all sessions where the judge is assigned on the same date and schedule
        sessions_with_judge = Session.objects.filter(
            date=session.date,  # Same date
            schedule=session.schedule,  # Same schedule
            judges__judge__in=judges  # Judge is assigned to the session
        ).exclude(id=session.id)  # Exclude the current session if it's an update

        # Check for time conflicts
        conflicting_sessions = sessions_with_judge.filter(
            Q(start_time__lt=session.end_time, end_time__gt=session.start_time)  # Time overlaps
        ).annotate(
            conflict_judge_first_name=F('judges__judge__first_name'),
            conflict_judge_last_name=F('judges__judge__last_name'), )

        if conflicting_sessions.exists():
            conflict = conflicting_sessions.first()
            e = (
                f"تداخل زمانی رخ داده است. داور {conflict.conflict_judge_first_name} {conflict.conflict_judge_last_name} در کلاس دیگری با شناسه ({conflict.id}) "
                f"در تاریخ {conflict.get_date_jalali} و بازه زمانی {conflict.start_time} تا {conflict.end_time} حضور دارد."
            )
            messages.error(self.request, f"خطا : {e}")
            raise ValidationError(
                f''
            )

    def validate_judges_as_professors_db(self, judges):
        session = self.instance
        # Filter all sessions on the same date and schedule, excluding the current session
        overlapping_sessions_2 = Session.objects.filter(
            date=session.date,  # Same date
            schedule=session.schedule,  # Same schedule
        ).exclude(id=session.id)  # Exclude the current session if it's an update

        # Find all conflicting sessions with any of the given judges
        conflicting_sessions = overlapping_sessions_2.filter(
            (
                    Q(supervisor1__in=judges) |
                    Q(supervisor2__in=judges) |
                    Q(supervisor3__in=judges) |
                    Q(supervisor4__in=judges) |
                    Q(graduate_monitor__in=judges)
            )
            & Q(start_time__lt=session.end_time, end_time__gt=session.start_time)  # Time overlaps
        )

        # If there are conflicts, raise a validation error
        if conflicting_sessions.exists():
            conflict_session = conflicting_sessions.annotate(
                conflict_field=Case(
                    When(supervisor1__in=judges,
                         then=Concat(F('supervisor1__first_name'), Value(' '), F('supervisor1__last_name'))),
                    # Concatenate first_name and last_name
                    When(supervisor2__in=judges,
                         then=Concat(F('supervisor2__first_name'), Value(' '), F('supervisor2__last_name'))),
                    When(supervisor3__in=judges,
                         then=Concat(F('supervisor3__first_name'), Value(' '), F('supervisor3__last_name'))),
                    When(supervisor4__in=judges,
                         then=Concat(F('supervisor4__first_name'), Value(' '), F('supervisor4__last_name'))),
                    When(graduate_monitor__in=judges, then=Concat(F('graduate_monitor__first_name'), Value(' '),
                                                                  F('graduate_monitor__last_name'))),
                    # Assuming graduate_monitor is a ForeignKey
                    default=Value('Unknown'),
                    output_field=CharField(),
                )
            ).first()
            e = (
                f"تداخل زمانی رخ داده است. استاد ({conflict_session.conflict_field}) در کلاس دیگری با شناسه ({conflict_session.id}) "
                f"در تاریخ {conflict_session.get_date_jalali} و بازه زمانی {conflict_session.start_time} تا {conflict_session.end_time} حضور دارد. (به عنوان استاد راهنما یا مشاور یا ناظر تحصیلات تکمیلی)"
            )
            messages.error(self.request, f"خطا : {e}")
            raise ValidationError(
                f''
            )

    def validate_professors_as_judges_db(self):
        session = self.instance  # Parent `Session` instance
        # Combine all professors into a single queryable list
        professors = [
            session.supervisor1,
            session.supervisor2,
            session.supervisor3,
            session.supervisor4,
            session.graduate_monitor,
        ]

        # Step 1: Filter for conflicting sessions
        conflicting_sessions = Session.objects.filter(
            date=session.date,  # Same date
            schedule=session.schedule,  # Same schedule
            judges__judge__in=professors,  # Judge is one of the professors
        ).exclude(id=session.id)  # Exclude the current session if it's an update

        # Step 2: Check for time conflicts
        conflicting_sessions = conflicting_sessions.filter(
            Q(start_time__lt=session.end_time, end_time__gt=session.start_time)  # Overlapping time
        )

        # Step 3: If conflicts exist, annotate only the first result
        if conflicting_sessions.exists():
            conflict = conflicting_sessions.annotate(
                conflict_professor=Case(
                    When(judges__judge=session.supervisor1,
                         then=Concat(F("judges__judge__first_name"), Value(" "), F("judges__judge__last_name"))),
                    When(judges__judge=session.supervisor2,
                         then=Concat(F("judges__judge__first_name"), Value(" "), F("judges__judge__last_name"))),
                    When(judges__judge=session.supervisor3,
                         then=Concat(F("judges__judge__first_name"), Value(" "), F("judges__judge__last_name"))),
                    When(judges__judge=session.supervisor4,
                         then=Concat(F("judges__judge__first_name"), Value(" "), F("judges__judge__last_name"))),
                    When(judges__judge=session.graduate_monitor,
                         then=Concat(F("judges__judge__first_name"), Value(" "), F("judges__judge__last_name"))),
                    default=Value("Unknown"),
                    output_field=CharField(),
                )
            ).first()
            e = (
                f"تداخل زمانی در اطلاعات برگزار کنندگان رخ داده است. استاد {conflict.conflict_professor} به عنوان داور در کلاس دیگری با شناسه ({conflict.id}) "
                f"در تاریخ {conflict.get_date_jalali} و بازه زمانی {conflict.start_time} تا {conflict.end_time} حضور دارد."
            )
            messages.error(self.request, f"خطا : {e}")
            raise ValidationError(
                f''
            )

    def validate_not_duplicate_judges_at_sameSession(self, judges):
        if len(judges) != len(set(judges)):
            e = (
                f"داوران در یک نشست نمیتوانند تکراری باشند"
            )
            messages.error(self.request, f"خطا : {e}")
            raise ValidationError(
                f''
            )

    def validate_not_duplicate_professors_and_judges_atSameSession(self, judges):
        # Validate against supervisors and graduate_monitor in the parent form
        parent_session = self.instance  # Parent `Session` instance
        for judge in judges:
            if judge in [
                v for v in [
                    parent_session.supervisor1,
                    parent_session.supervisor2,
                    parent_session.supervisor3,
                    parent_session.supervisor4,
                    parent_session.graduate_monitor]
                if v != None
            ]:
                e = (f"داور {judge} نمی‌تواند یکی از اساتید یا ناظر در همین نشست باشد.")
                messages.error(self.request, f"خطا : {e}")
                raise ValidationError(
                    f''
                )


class JudgeAssignmentInline(admin.TabularInline):
    model = JudgeAssignment
    form = JudgeAssignmentForm  # Attach the custom form
    formset = JudgeAssignmentFormSet
    extra = 1  # Number of empty rows to show for adding new judges
    verbose_name = "داور"
    verbose_name_plural = "بخش هیئت داوران"
    autocomplete_fields = ['judge']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('judge', 'session')  # Optimize related field

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(JudgeAssignmentInline, self).get_formset(request, obj, **kwargs)
        formset.request = request
        return formset


class SessionAdminForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):  # ✅ Accept args and kwargs
        super(SessionAdminForm, self).__init__(*args, **kwargs)
        match self.request.user.role:
            case 'ALL':
                qs__faculty_educational_group = FacultyEducationalGroup.objects.all()
                self.fields['faculty_educational_group'].queryset = qs__faculty_educational_group

                qs__student = Student.objects.all()
                self.fields['student'].queryset = qs__student

            case _:
                qs__faculty_educational_group = FacultyEducationalGroup.objects.\
                    filter(faculty=self.request.user.role)
                self.fields['faculty_educational_group'].queryset = qs__faculty_educational_group

                qs__student = Student.objects.filter(faculty_educational_group__faculty=self.request.user.role)
                self.fields['student'].queryset = qs__student

        self.fields['faculty_educational_group'].empty_label = None
        self.fields['student'].empty_label = None

    class Meta:
        model = Session
        fields = '__all__'
        widgets = {
            'date': AdminJalaliDateWidget,  # Jalali date picker
            'start_time': TimePickerInput,  # Time picker
            'end_time': TimePickerInput,  # Time picker
        }

    def clean(self):
        cleaned_data = super(SessionAdminForm, self).clean()
        self.sessionID = self.instance.id
        self.start_time = cleaned_data.get('start_time')
        self.end_time = cleaned_data.get('end_time')
        self.date = cleaned_data.get('date')
        self.schedule = cleaned_data.get('schedule')
        self.student = cleaned_data.get('student')
        self.supervisor1 = cleaned_data.get('supervisor1')
        self.supervisor2 = cleaned_data.get('supervisor2')
        self.supervisor3 = cleaned_data.get('supervisor3')
        self.supervisor4 = cleaned_data.get('supervisor4')
        self.graduate_monitor = cleaned_data.get('graduate_monitor')
        self.class_number = cleaned_data.get('class_number')
        self.faculty_educational_group = cleaned_data.get('faculty_educational_group')

        self.validate_empty_fields()

        if self.start_time >= self.end_time:
            messages.error(self.request, "خطا در اطلاعات جلسه دفاعیه. تاریخ شروع جلسه باید قبل از تاریخ پایان باشد !")
            raise forms.ValidationError(f'')

        # Filter sessions with the same date and schedule, excluding the current session
        overlapping_sessions = Session.objects.filter(
            date=self.date,
            schedule=self.schedule,
        ).exclude(id=self.sessionID)

        # validate overlaping sessions
        self.validate_overlapingSessions()

        # Validate professors (supervisors and graduate monitor)
        roles = [
            self.supervisor1, self.supervisor2, self.supervisor3, self.supervisor4,
            self.graduate_monitor
        ]
        self.validate_professors(roles, overlapping_sessions)

        self.valiadte_students(overlapping_sessions)

    def validate_empty_fields(self):
        if self.start_time == None or self.end_time == None or self.student == None\
                or self.class_number == None or self.supervisor1 == None or self.graduate_monitor == None\
                or self.faculty_educational_group == None:
            raise ValidationError(f'')

    def valiadte_students(self, overlapping_sessions):
        # Find all conflicting sessions with any of the given student
        conflicting_sessions = overlapping_sessions.filter(
            (
                    Q(student=self.student)
            )
            & Q(start_time__lt=self.end_time, end_time__gt=self.start_time)  # Time overlaps
        )
        if conflicting_sessions.exists():
            conflict_session = conflicting_sessions.first()
            messages.error(self.request,
                f"تداخل زمانی در اطلاعات برگزار کنندگان رخ داده است. دانشجو ({conflict_session.student}) در کلاس دیگری با شناسه ({conflict_session.id}) "
                f"در تاریخ {conflict_session.get_date_jalali} و بازه زمانی {conflict_session.start_time} تا {conflict_session.end_time} حضور دارد.")
            raise forms.ValidationError(f'')

    def validate_overlapingSessions(self):
        # Check for time conflicts in the same term (date) and schedule and class_number
        overlapping_sessions = Session.objects.filter(
            date=self.date,  # Same term/date
            schedule=self.schedule,  # Same semester
            class_number=self.class_number,  #Same class
        ).exclude(id=self.sessionID)  # Exclude the current session if it's an update

        # Check if the start and end times of the current session overlap with any existing session
        for session in overlapping_sessions:
            # Time overlap condition:
            # 1. The current session starts during another session.
            # 2. The current session ends during another session.
            # 3. The current session completely spans another session.
            if (
                    (self.start_time >= session.start_time and self.start_time < session.end_time) or
                    (self.end_time > session.start_time and self.end_time <= session.end_time) or
                    (self.start_time <= session.start_time and self.end_time >= session.end_time)
            ):
                messages.error(self.request, f"این نشست تداخل زمانی دارد با نشست دیگری با شناسه {session.id} در تاریخ {session.get_date_jalali} در بازه زمانی {session.start_time} - {session.end_time} ")
                raise forms.ValidationError(f"")

    def validate_professors(self, roles, overlapping_sessions):
        # Remove any None values (empty fields)
        professors = [prof for prof in roles if prof is not None]

        # Check for duplicates
        if len(professors) != len(set(professors)):
            messages.error(self.request,
                           "اساتید حاظر در اطلاعات برگزار کنندگان (استاد راهنما یا مشاور یا ناظر تحصیلات تکمیلی) نمی‌توانند در یک نشست تکراری باشند."
                           )
            raise forms.ValidationError(f"")


        # Find all conflicting sessions with any of the given professors
        conflicting_sessions = overlapping_sessions.filter(
            (
                    Q(supervisor1__in=professors) |
                    Q(supervisor2__in=professors) |
                    Q(supervisor3__in=professors) |
                    Q(supervisor4__in=professors) |
                    Q(graduate_monitor__in=professors)
            )
            & Q(start_time__lt=self.end_time, end_time__gt=self.start_time)  # Time overlaps
        )

        # Check if any conflicts exist
        if conflicting_sessions.exists():

            conflict_session = conflicting_sessions.annotate(
                conflict_professor=Case(
                    When(supervisor1__in=professors, then=Concat(F('supervisor1__first_name'), Value(' '), F('supervisor1__last_name'))),
                    When(supervisor2__in=professors, then=Concat(F('supervisor2__first_name'), Value(' '), F('supervisor2__last_name'))),
                    When(supervisor3__in=professors, then=Concat(F('supervisor3__first_name'), Value(' '), F('supervisor3__last_name'))),
                    When(supervisor4__in=professors, then=Concat(F('supervisor4__first_name'), Value(' '), F('supervisor4__last_name'))),
                    When(graduate_monitor__in=professors,
                         then=Concat(F('graduate_monitor__first_name'), Value(' '), F('graduate_monitor__last_name'))),
                    default=Value(''),
                    output_field=CharField(),
                )
            ).first()

            messages.error(self.request,
                           f"تداخل زمانی در اطلاعات برگزار کنندگان رخ داده است. استاد ({conflict_session.conflict_professor}) در کلاس دیگری با شناسه ({conflict_session.id}) "
                           f"در تاریخ {conflict_session.get_date_jalali} و بازه زمانی {conflict_session.start_time} تا {conflict_session.end_time} حضور دارد."
            )
            raise forms.ValidationError(f'')


class SessionAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    form = SessionAdminForm
    inlines = [JudgeAssignmentInline]
    # Fields to be displayed in the list view
    list_display = ('edit_session', 'get_id', 'student', 'get_student_role', 'schedule', 'faculty_educational_group', 'get_date_jalali',
                    'get_start_time_persian', 'get_end_time_persian',
                    'get_class_number',
                    'get_judges_number_assigned',
                    'session_status',
                    'get_updated_at_jalali',)

    # Fields to be used for searching in the admin interface
    search_fields = ('student__first_name', 'student__last_name', 'supervisor1__first_name',
                     'supervisor1__last_name',
                     'supervisor2__first_name',
                     'supervisor2__last_name',
                     'supervisor3__first_name',
                     'supervisor3__last_name',
                     'supervisor4__first_name',
                     'supervisor4__last_name',
                     'id')

    # Filters to narrow down results in the list view
    list_filter = ('session_status', 'is_active', MonthFilter_created_at,
                   MonthFilter_updated_at,
                   SupervisorCountFilter,
                   Consultant_ProfessorCountFilter,
                   )

    autocomplete_fields = [
        'supervisor1', 'supervisor2', 'supervisor3', 'supervisor4', 'graduate_monitor',
    ]

    # Make sure the fields are read-only in certain cases, or configure which ones can be modified
    readonly_fields = ('get_created_at_jalali',
                       'get_updated_at_jalali',
                       'is_active', 'created_by', 'updated_by')

    # Fieldsets to group fields logically in the form view

    # class Media:
    #     js = ('js/admin_assignment_session/filter_supervisors.js',
    #           'js/admin_assignment_session/filter_graduate_monitor.js',
    #           'js/admin_assignment_session/filter_judges.js',)

    # Add a custom URL to the admin panel
    change_form_template = 'assignment/admin/change_form.html'

    def edit_session(self, obj):
        return format_html('<a href="{}">مشاهده</a>', f"/admin/assignment/session/{obj.id}/change/")
    edit_session.short_description = "اطلاعات کامل جلسه دفاعیه"

    def get_list_display_links(self, request, list_display):
        # Remove links from all columns
        return ('edit_educationl_group')  # Keep the link only on `edit_teacher`

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('download_session', self.admin_site.admin_view(self.download_session), name='download_session'),
        ]
        return custom_urls + urls

    # Add a button/link in the admin toolbar
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        name = "دانلود گزارش جلسه ها به صورت فایل Excel"
        extra_context['custom_button'] = format_html(
            f'<a class="button" href="download_session">{name}</a>'
        )
        return super().changelist_view(request, extra_context=extra_context)

    def download_session(self, request):
        if request.method == "POST":  # If the user clicks "Download CSV"
            schedule_filter = request.POST.get('schedule', None)
            faculty_filter = request.POST.get('faculty', None)
            # Query the filtered data
            if schedule_filter and faculty_filter:
                if faculty_filter == "10":
                    sessions = Session.objects.filter(schedule=schedule_filter)
                else:
                    sessions = Session.objects.filter(schedule=schedule_filter, faculty_educational_group=faculty_filter)
            else:
                sessions = Session.objects.all()

            # Create a workbook and add a worksheet
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Schedules"

            # Write the header row (with Persian text)
            sheet.append(["دانشکده و گروه آموزشی" , 'سال', 'نیم‌سال', 'تاریخ', 'ساعت شروع', 'ساعت پایان',
                          'دانشجو', 'استاد راهنما اول', 'استاد راهنما دوم',
                          'استاد مشاور اول', 'استاد مشاور دوم', 'ناظر تحصیلات تکمیلی',
                          "داوران حاضر در این نشست"])
            for session in sessions:
                # Append each schedule as a row
                sheet.append([
                    session.faculty_educational_group.title,
                    session.schedule.year,
                    session.schedule.get_semester_display(),
                    date2jalali(session.date).strftime('%a, %d %b %Y'),
                    session.start_time,
                    session.end_time,
                    session.student.name,
                    session.supervisor1.name,
                    session.supervisor2.name if session.supervisor2 else None,
                    session.supervisor3.name if session.supervisor3 else None,
                    session.supervisor4.name if session.supervisor4 else None,
                    session.graduate_monitor.name,
                    # Get the names of all judges assigned to this session
                    ", ".join(judge_assignment.judge.name for judge_assignment in session.judges.all())
                ])
            # Prepare the response as an Excel file
            filename = f"schedules"
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'

            # Save the workbook to the response
            workbook.save(response)
            return response

        find_all_schedules = Schedule.objects.all()
        find_all_faculty = FacultyEducationalGroup.objects.filter(faculty=request.user.role)

        # If the user accesses the page
        return render(request, 'assignment/download_session.html', {
            'schedules': find_all_schedules,
            'faculty_list': find_all_faculty,
            'faculty_name': FacultyEducationalGroup.objects.filter(faculty=request.user.role).last(),
        })

    def get_fieldsets(self, request, obj=None):
        title = ""
        match request.user.role:
            case 'ALL':
                title = "(تمام دانشجویان)"
            case _:
                title = f" از مجموعه دانشجویان {self.FACULTY_CHOICES_DICT[request.user.role]}"
        # If `obj` is None, it's the Add view
        if obj is None:
            # Exclude the "سایر اطلاعات" fieldset
            return (
                (_('اطلاعات جلسه دفاعیه'), {
                    'fields': ('schedule', 'date', 'start_time', 'end_time', 'faculty_educational_group', 'class_number')
                }),
                (_(f"اطلاعات دانشجو - {title}"), {
                    'fields': (
                        'student',
                    )
                }),
                (_('اطلاعات استاد راهنما'), {
                    'fields': (
                        'supervisor1', 'supervisor2'
                    )
                }),
                (_('اطلاعات استاد مشاور'), {
                    'fields': (
                        'supervisor3',
                        'supervisor4',
                    )
                }),
                (_('اطلاعات ناظر تحصیلات تکمیلی'), {
                    'fields': (
                        'graduate_monitor',
                    )
                }),
                (_('اطلاعات اضافی'), {
                    'fields': ('description',
                               ),
                    'classes': ('collapse',),

                })
            )
        # Show all fieldsets (default) in the Change view
        else:
            match request.user.is_superuser:
                case True:
                    return (
                        (_('اطلاعات جلسه دفاعیه'), {
                            'fields': ('schedule', 'date', 'start_time', 'end_time',
                                       'faculty_educational_group', 'class_number'),
                            'description': _("""
                                ✅
                    نیم سال تحصیلی / تاریخ / زمان شروع و زمان پایان جلسه / شماره کلاس را به گونه انتخاب کنید تا تداخل ایجاد نشود.         ⚠️      
                    در غیر این صورت با پیغام خطا مواجه خواهید شد.               
                                """)
                        }),
                        (_(f"{title} اطلاعات دانشجو - "), {
                            'fields': (
                                'student',
                            )
                        }),
                        (_('اطلاعات استاد راهنما'), {
                            'fields': (
                                'supervisor1', 'supervisor2'
                            )
                        }),
                        (_('اطلاعات استاد مشاور'), {
                            'fields': (
                                'supervisor3',
                                'supervisor4',
                            )
                        }),
                        (_('اطلاعات ناظر تحصیلات تکمیلی'), {
                            'fields': (
                                'graduate_monitor',
                            )
                        }),
                        (_('تاریخ ایجاد / ویرایش این جلسه'), {
                            'fields': ('get_created_at_jalali',
                                       'created_by',
                                       'get_updated_at_jalali',
                                       'updated_by',
                                       )
                        }),
                        (_('اطلاعات اضافی'), {
                            'fields': ('description', 'session_status'
                                       ),
                            'classes': ('collapse',),
                        })
                    )
                case False:
                    return (
                        (_('اطلاعات جلسه دفاعیه'), {
                            'fields': ('schedule', 'date', 'start_time', 'end_time', 'class_number'),
                            'description': _("""
                        ✅
            نیم سال تحصیلی / تاریخ / زمان شروع و زمان پایان جلسه / شماره کلاس را به گونه انتخاب کنید تا تداخل ایجاد نشود.         ⚠️      
            در غیر این صورت با پیغام خطا مواجه خواهید شد.               
                        """)
                        }),
                        (_(f"{title} اطلاعات دانشجو - "), {
                            'fields': (
                                'student',
                            )
                        }),
                        (_('اطلاعات استاد راهنما'), {
                            'fields': (
                                'supervisor1', 'supervisor2'
                            )
                        }),
                        (_('اطلاعات استاد مشاور'), {
                            'fields': (
                                'supervisor3',
                                'supervisor4',
                            )
                        }),
                        (_('اطلاعات ناظر تحصیلات تکمیلی'), {
                            'fields': (
                                'graduate_monitor',
                            )
                        }),
                        (_('تاریخ ایجاد / ویرایش این جلسه'), {
                            'fields': ('get_created_at_jalali',
                                       'created_by',
                                       'get_updated_at_jalali',
                                       'updated_by',
                                       )
                        }),
                        (_('اطلاعات اضافی'), {
                            'fields': ('description',
                                       ),
                            'classes': ('collapse',),
                        })
                    )

        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        # If `obj` is None, it's the "Add" view; otherwise, it's the "Change" view
        if obj is None:
            # Return an empty list of readonly fields in the Add view
            return []
        return self.readonly_fields

    def get_form(self, request, *args, **kwargs):
        form = super(SessionAdmin, self).get_form(request, *args, **kwargs)
        form.request = request  # Pass the request object to the form
        return form

    @admin.display(description='شناسه', ordering='id')
    def get_id(self, obj):
        return obj.id

    @admin.display(description='مقطع تحصیلی')
    def get_student_role(self, obj):
        ROLES_DICT = {
            'Ph.D.': 'دکتری',
            'Master': 'ارشد',
        }
        return ROLES_DICT[obj.student.role]

    @admin.display(description='شماره کلاس')
    def get_class_number(self, obj):
        return obj.class_number

    @admin.display(description='تعداد داوران')
    def get_judges_number_assigned(self, obj):
        return obj.judges.count()

    @admin.display(description='ایجاد شده در زمان/تاریخ', ordering='created_at')
    def get_created_at_jalali(self, obj):
        if obj.created_at:
            return datetime2jalali(obj.created_at).strftime('%a, %d %b %Y | %H:%M:%S')
        else:
            return "ثبت نشده است"

    @admin.display(description='آخرین ویرایش در زمان/تاریخ', ordering='updated_at')
    def get_updated_at_jalali(self, obj):
        if obj.updated_at:
            return datetime2jalali(obj.updated_at).strftime('%a, %d %b %Y | %H:%M:%S')
        else:
            return "ثبت نشده است"

    @admin.display(description='تاریخ برگزاری جلسه', ordering='date')
    def get_date_jalali(self, obj):
        if obj.date:
            return date2jalali(obj.date).strftime('%a, %d %b %Y')
        else:
            return "ثبت نشده است"

    @admin.display(description="زمان شروع", ordering="satrt_time")
    def get_start_time_persian(self, obj):
        if obj.start_time:
            # Convert time to Persian 12-hour format
            time = obj.start_time
            hour = time.hour
            minute = f'{time.minute}'.zfill(2)

            # Determine AM/PM and adjust the hour
            match hour:
                case 0:
                    period = "بامداد"
                    hour = 12
                case 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11:
                    period = "صبح"
                case 12:
                    period = "ظهر"
                    hour = 12
                case 13 | 14 | 15 | 16:
                    period = "ظهر"
                    hour -= 12
                case _:
                    period = "عصر"
                    hour -= 12

            return f"{hour}:{minute} ظهر "
        else:
            return "ثبت نشده است"

    @admin.display(description="زمان پایان", ordering="end_time")
    def get_end_time_persian(self, obj):
        if obj.end_time:
            # Convert time to Persian 12-hour format
            time = obj.end_time
            hour = time.hour
            minute = f'{time.minute}'.zfill(2)

            # Determine AM/PM and adjust the hour
            match hour:
                case 0:
                    period = "بامداد"
                    hour = 12
                case 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11:
                    period = "صبح"
                case 12:
                    period = "ظهر"
                    hour = 12
                case 13 | 14 | 15 | 16:
                    period = "ظهر"
                    hour -= 12
                case _:
                    period = "عصر"
                    hour -= 12

            return f"{hour}:{minute} ظهر "
        else:
            return "ثبت نشده است"

    def save_model(self, request, obj, form, change):
        if not obj.created_by:  # If created_by is not set, assign the current user
            obj.created_by = request.user.name
        obj.updated_by = request.user.user_info  # Always set updated_by to the current user

        # Save the object
        obj.save()

# Register the Session model with the custom admin class
admin.site.register(Session, SessionAdmin)
