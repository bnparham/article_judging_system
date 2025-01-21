from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet

from jalali_date import datetime2jalali, date2jalali
from jalali_date.admin import ModelAdminJalaliMixin

from .models import Session, JudgeAssignment
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django import forms
from jalali_date.widgets import AdminJalaliDateWidget
from django_flatpickr.widgets import TimePickerInput  # Import Flatpickr widget

class MonthFilter(admin.SimpleListFilter):
    title = _('بر اساس زمانبدی نشست')
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        return (
            ('1', _('دی')),
            ('2', _('بهمن')),
            ('3', _('اسفند')),
            ('4', _('فروردین')),
            ('5', _('اردیبهشت')),
            ('6', _('خرداد')),
            ('7', _('تیر')),
            ('8', _('مرداد')),
            ('9', _('شهریور')),
            ('10', _('مهر')),
            ('11', _('آبان')),
            ('12', _('آذر')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if(hasattr(queryset.model, 'schedule')):
                return queryset.filter(schedule__date__month=self.value())


class MonthFilter_created_at(admin.SimpleListFilter):
    title = _('بر اساس زمان ایجاد شده ')
    parameter_name = 'month_created_at'

    def lookups(self, request, model_admin):
        return (
            ('1', _('دی')),
            ('2', _('بهمن')),
            ('3', _('اسفند')),
            ('4', _('فروردین')),
            ('5', _('اردیبهشت')),
            ('6', _('خرداد')),
            ('7', _('تیر')),
            ('8', _('مرداد')),
            ('9', _('شهریور')),
            ('10', _('مهر')),
            ('11', _('آبان')),
            ('12', _('آذر')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if(hasattr(queryset.model, 'created_at')):
                return queryset.filter(created_at__month=self.value())

class MonthFilter_updated_at(admin.SimpleListFilter):
    title = _('بر اساس زمان ویرایش شده')
    parameter_name = 'month_updated_at'

    def lookups(self, request, model_admin):
        return (
            ('1', _('دی')),
            ('2', _('بهمن')),
            ('3', _('اسفند')),
            ('4', _('فروردین')),
            ('5', _('اردیبهشت')),
            ('6', _('خرداد')),
            ('7', _('تیر')),
            ('8', _('مرداد')),
            ('9', _('شهریور')),
            ('10', _('مهر')),
            ('11', _('آبان')),
            ('12', _('آذر')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if(hasattr(queryset.model, 'updated_at')):
                return queryset.filter(updated_at__month=self.value())

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
                supervisor4__isnull=False,) |
                Q(supervisor3__isnull=False,
                supervisor4__isnull=True,)
            )
        elif self.value() == '2':
            return queryset.filter(
                supervisor3__isnull=False,
                supervisor4__isnull=False,
            )
        return queryset

class JudgesCountFilter(admin.SimpleListFilter):
    title = _('تعداد داوران')
    parameter_name = 'Judges_count'

    def lookups(self, request, model_admin):
        return [
            ('0', _('بدون داور')),
            ('1', _('یک داور')),
            ('2', _('دو داور')),
            ('3', _('سه داور')),
        ]

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(
                judge1__isnull=True,
                judge2__isnull=True,
                judge3__isnull=True,
            )
        elif self.value() == '1':
            return queryset.filter(
                Q(judge1__isnull=False,
                  judge2__isnull=True,
                  judge3__isnull=True,) |
                Q(judge1__isnull=True,
                  judge2__isnull=False,
                  judge3__isnull=True,) |
                Q(judge1__isnull=True,
                  judge2__isnull=True,
                  judge3__isnull=False,)
            )
        elif self.value() == '2':
            return queryset.filter(
                Q(judge1__isnull=False,
                  judge2__isnull=False,
                  judge3__isnull=True,) |
                Q(judge1__isnull=False,
                  judge2__isnull=True,
                  judge3__isnull=False,) |
                Q(judge1__isnull=True,
                  judge2__isnull=False,
                  judge3__isnull=False,)
            )
        elif self.value() == '3':
            return queryset.filter(
                Q(judge1__isnull=False,
                  judge2__isnull=False,
                  judge3__isnull=False,)
            )
        return queryset


class JudgeAssignmentForm(forms.ModelForm):

    class Meta:
        model = JudgeAssignment
        fields = ['judge']

    def clean(self):

        cleaned_data = super().clean()  # Always call the parent clean method

        judge_field = cleaned_data.get('judge')  # Access the 'judge' field specifically

        self.validate_judges(judge_field)

        self.validate_judges_as_professors(judge_field)

        return cleaned_data

    def validate_judges(self, judge):

        session = self.instance.session  # Assuming you have a 'session' field in JudgeAssignment

        # Find all sessions where the judge is assigned on the same date and schedule
        sessions_with_judge = Session.objects.filter(
            date=session.date,  # Same date
            schedule=session.schedule,  # Same schedule
            judges__judge=judge  # Judge is assigned to the session
        ).exclude(id=session.id)  # Exclude the current session if it's an update

        # Check for time conflicts
        conflicting_sessions = sessions_with_judge.filter(
            Q(start_time__lt=session.end_time, end_time__gt=session.start_time)  # Time overlaps
        )

        if conflicting_sessions.exists():
            session = conflicting_sessions.first()
            raise ValidationError(
                f"تداخل زمانی رخ داده است. داور {judge} در کلاس دیگری با شناسه ({session.id}) "
                f"در تاریخ {session.get_date_jalali} و بازه زمانی {session.start_time} تا {session.end_time} حضور دارد."
            )

    def validate_judges_as_professors(self, judge):

        session = self.instance.session  # Assuming you have a 'session' field in JudgeAssignment

        overlapping_sessions_2 = Session.objects.filter(
            date=session.date,  # Same term/date
            schedule=session.schedule,  # Same semester
        ).exclude(id=session.id)  # Exclude the current session if it's an update

        conflicting_sessions = overlapping_sessions_2.filter(
            (
                    Q(supervisor1=judge) | Q(supervisor2=judge) |
                    Q(supervisor3=judge) | Q(supervisor4=judge) |
                    Q(graduate_monitor=judge)
            )
            & (
                Q(start_time__lt=session.end_time, end_time__gt=session.start_time)  # Time overlaps
            )
        )

        if conflicting_sessions.exists():
            session = conflicting_sessions.first()
            raise ValidationError(
                f"تداخل زمانی رخ داده است. داور {judge} به عنوان استاد مشاور یا ناظر تحصیلات تکمیلی در کلاس دیگری با شناسه {session.id} در تاریخ {session.get_date_jalali} و بازه زمانی {session.start_time} تا {session.end_time} حضور دارد."
            )


class JudgeAssignmentFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        # Judges will be accessible here if you need to validate only within the inline formset
        self.judges = [
            form.cleaned_data.get('judge')
            for form in self.forms
            if not form.cleaned_data.get('DELETE', False)  # Exclude deleted judges
        ]
        if len(self.judges) != len(set(self.judges)):
            raise ValidationError(
                f"داوران در یک نشست نمیتوانند تکراری باشند"
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

class SessionAdminForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = '__all__'
        widgets = {
            'date': AdminJalaliDateWidget,  # Jalali date picker
            'start_time': TimePickerInput,  # Time picker
            'end_time': TimePickerInput,  # Time picker
        }

class SessionAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    form = SessionAdminForm
    inlines = [JudgeAssignmentInline]
    # Fields to be displayed in the list view
    list_display = ('get_id', 'student', 'schedule', 'get_date_jalali',
                    'get_start_time_persian', 'get_end_time_persian',
                    'class_number',
                    'session_status',
                    'get_updated_at_jalali')

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
    list_filter = ('session_status', 'is_active', MonthFilter, MonthFilter_created_at,
                   MonthFilter_updated_at,
                   SupervisorCountFilter,
                   Consultant_ProfessorCountFilter,
                   )

    autocomplete_fields = [
                     'supervisor1', 'supervisor2', 'supervisor3', 'supervisor4', 'graduate_monitor',
    ]

    # Make sure the fields are read-only in certain cases, or configure which ones can be modified
    readonly_fields = ('get_created_at_jalali', 'get_updated_at_jalali', 'is_active')

    # Fieldsets to group fields logically in the form view
    fieldsets = (
        (_('اطلاعات جلسه دفاعیه'), {
            'fields': ('schedule', 'date', 'start_time', 'end_time', 'class_number'),
            'description': _("""
            ✅
نیم سال تحصیلی / تاریخ / زمان شروع و زمان پایان جلسه / شماره کلاس را به گونه انتخاب کنید تا تداخل ایجاد نشود.         ⚠️      
در غیر این صورت با پیغام خطا مواجه خواهید شد               
            """)
        }),
        (_('اطلاعات برگزار کنندگان'), {
            'fields': ('student', 'supervisor1', 'supervisor2', 'supervisor3',
                       'supervisor4', 'graduate_monitor',)
        }),
        (_('تاریخ ایجاد / ویرایش این جلسه'), {
            'fields': ('get_created_at_jalali',
                       'get_updated_at_jalali',
                       )
        }),
        (_('اطلاعات اضافی'), {
            'fields': ('description',
                       ),
            'classes': ('collapse',),
        })
    )

    # class Media:
    #     js = ('js/admin_assignment_session/filter_supervisors.js',
    #           'js/admin_assignment_session/filter_graduate_monitor.js',
    #           'js/admin_assignment_session/filter_judges.js',)


    # def get_form(self, request, obj=None, **kwargs):
    #     """
    #     Override get_form to dynamically filter the supervisor fields based on the selected schedule.
    #     """
    #     form = super().get_form(request, obj, **kwargs)
    #
    #     if obj and obj.pk is not None:
    #         current_session_schedule = obj.schedule  # Current session's schedule
    #         current_session_id = obj.pk  # Current session ID
    #
    #         self.filter_supervisor_fields_queryset(request, obj, current_session_schedule,
    #                                                current_session_id, form, **kwargs)
    #
    #         self.filter_graduate_monitor_fields_queryset(request, obj, current_session_schedule,
    #                                                current_session_id, form, **kwargs)
    #
    #         self.filter_judges_fields_queryset(request, obj, current_session_schedule,
    #                                                current_session_id, form, **kwargs)
    #
    #     return form

    def save_related(self, request, form, formsets, change):

        self.find_JudgeAssignmentForm = None
        self.find_judges_inline_form = []
        super().save_related(request, form, formsets, change)

        # Access related `JudgeAssignment` objects
        for formset in formsets:
            if formset.model == JudgeAssignment:
                self.find_JudgeAssignmentForm = formset
                for inline_form in formset.forms:

                    judge_assignment_instance = inline_form.instance

                    # Ensure the instance is valid and saved before accessing its fields
                    if judge_assignment_instance.pk:  # Check if the instance is saved
                        # print(f"Judge Assignment: {judge_assignment_instance}")
                        # print(f"Assigned Judge: {judge_assignment_instance.judge}")
                        self.find_judges_inline_form.append(judge_assignment_instance.judge)
                    else:
                        # this is happen for empty fields !
                        # print("Instance not saved yet or incomplete.")
                        continue

        # Validate find_judges_inline_form with Session Fields (supervisors, graduate_monitor) !

        supervisor1 = form.cleaned_data.get('supervisor1')
        supervisor2 = form.cleaned_data.get('supervisor2')
        supervisor3 = form.cleaned_data.get('supervisor3')
        supervisor4 = form.cleaned_data.get('supervisor4')
        graduate_monitor = form.cleaned_data.get('graduate_monitor')

        supervisors_and_monitors = {
            supervisor1,
            supervisor2,
            supervisor3,
            supervisor4,
            graduate_monitor,
        }
        supervisors_and_monitors.discard(None)  # Remove None values

        print(supervisors_and_monitors, self.find_judges_inline_form)

        for person in supervisors_and_monitors:
            if person in self.find_judges_inline_form:
                e = f"شخص {person} نمی‌تواند هم به عنوان داور و هم به عنوان استاد مشاور یا ناظر تحصیلات تکمیلی باشد."

                # Show the error message in the admin panel
                self.message_user(request, str(e), level='error')
                # Add the error to the form so it prevents saving
                form.add_error(None, e)  # Add the error to the non-field errors
                # Prevent the save from happening by returning early
                self.find_JudgeAssignmentForm.save(commit=False)
                return

                # Prevent the save from happening by returning early




    def get_fieldsets(self, request, obj=None):
        # If `obj` is None, it's the Add view
        if obj is None:
            # Exclude the "سایر اطلاعات" fieldset
            return (
                (_('اطلاعات جلسه دفاعیه'), {
                    'fields': ('schedule', 'date', 'start_time', 'end_time', 'class_number')
                }),
                (_('اطلاعات برگزار کنندگان'), {
                    'fields': (
                    'student', 'supervisor1', 'supervisor2', 'supervisor3',
                    'supervisor4', 'graduate_monitor',
                    )
                }),
                # (_('بخش هیئت داوران'), {
                #     'fields': (
                #         'judge1', 'judge2', 'judge3',
                #     )
                # }),
                (_('اطلاعات اضافی'), {
                    'fields': ('description',
                               ),
                    'classes': ('collapse',),

                })
            )
        # Show all fieldsets (default) in the Change view
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        # If `obj` is None, it's the "Add" view; otherwise, it's the "Change" view
        if obj is None:
            # Return an empty list of readonly fields in the Add view
            return []
        return self.readonly_fields

    @admin.display(description='شناسه', ordering='id')
    def get_id(self, obj):
        return obj.id

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

    @admin.display(description='تاریخ', ordering='date')
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


    def filter_supervisor_fields_queryset(self, request, obj,
                                          current_session_schedule,
                                          current_session_id, form,
                                          **kwargs):
        supervisor_fields = ['supervisor1', 'supervisor2', 'supervisor3', 'supervisor4']
        for field_name in supervisor_fields:
            field = form.base_fields[field_name]
            query_assigned_to_current = field.queryset.filter(
                Q(supervisor1_assignments__schedule=current_session_schedule,
                  supervisor1_assignments__id=current_session_id) |
                Q(supervisor2_assignments__schedule=current_session_schedule,
                  supervisor2_assignments__id=current_session_id) |
                Q(supervisor3_assignments__schedule=current_session_schedule,
                  supervisor3_assignments__id=current_session_id) |
                Q(supervisor4_assignments__schedule=current_session_schedule,
                  supervisor4_assignments__id=current_session_id)
            )

            # Query to exclude supervisors assigned to the same schedule in other sessions
            query_not_in_other_sessions = field.queryset.filter(
                ~Q(supervisor1_assignments__schedule=current_session_schedule) &
                ~Q(supervisor2_assignments__schedule=current_session_schedule) &
                ~Q(supervisor3_assignments__schedule=current_session_schedule) &
                ~Q(supervisor4_assignments__schedule=current_session_schedule)
            )

            # Combine the two querysets and remove duplicates
            combined_queryset = query_assigned_to_current | query_not_in_other_sessions

            # Assign the combined queryset to the field
            field.queryset = combined_queryset.distinct()

    def filter_graduate_monitor_fields_queryset(self, request, obj,
                                          current_session_schedule,
                                          current_session_id, form,
                                          **kwargs):
        graduate_monitor_fields = ['graduate_monitor']
        for field_name in graduate_monitor_fields:
            field = form.base_fields[field_name]
            query_assigned_to_current = field.queryset.filter(
                Q(graduate_monitor_assignments__schedule=current_session_schedule,
                  graduate_monitor_assignments__id=current_session_id)
            )

            # Query to exclude supervisors assigned to the same schedule in other sessions
            query_not_in_other_sessions = field.queryset.filter(
                ~Q(graduate_monitor_assignments__schedule=current_session_schedule)
            )

            # Combine the two querysets and remove duplicates
            combined_queryset = query_assigned_to_current | query_not_in_other_sessions

            # Assign the combined queryset to the field
            field.queryset = combined_queryset.distinct()

    def filter_judges_fields_queryset(self, request, obj,
                                          current_session_schedule,
                                          current_session_id, form,
                                          **kwargs):
        judges_fields = ['judge1', 'judge2', 'judge3']
        for field_name in judges_fields:
            field = form.base_fields[field_name]
            query_assigned_to_current = field.queryset.filter(
                Q(judge1_assignments__schedule=current_session_schedule,
                  judge1_assignments__id=current_session_id) |
                Q(judge2_assignments__schedule=current_session_schedule,
                  judge2_assignments__id=current_session_id) |
                Q(judge3_assignments__schedule=current_session_schedule,
                  judge3_assignments__id=current_session_id)
            )

            # Query to exclude supervisors assigned to the same schedule in other sessions
            query_not_in_other_sessions = field.queryset.filter(
                ~Q(judge1_assignments__schedule=current_session_schedule) &
                ~Q(judge2_assignments__schedule=current_session_schedule) &
                ~Q(judge3_assignments__schedule=current_session_schedule)
            )

            # Combine the two querysets and remove duplicates
            combined_queryset = query_assigned_to_current | query_not_in_other_sessions

            # Assign the combined queryset to the field
            field.queryset = combined_queryset.distinct()



    def save_model(self, request, obj, form, change):
        try:
            obj.clean()  # Call the custom clean method before saving

        except ValidationError as e:
            # Catch the validation error and display it
            self.message_user(request, str(e), level='error')
            return  # Don't save the model if validation fails
        super().save_model(request, obj, form, change)  # Save if no error

# Register the Session model with the custom admin class
admin.site.register(Session, SessionAdmin)
