from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db.models.functions import Concat
from django.forms import BaseInlineFormSet
from django.shortcuts import redirect

from jalali_date import datetime2jalali, date2jalali
from jalali_date.admin import ModelAdminJalaliMixin

from .models import Session, JudgeAssignment
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, F, Case, When, Value, CharField
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
            if (hasattr(queryset.model, 'schedule')):
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
            if (hasattr(queryset.model, 'created_at')):
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
            if (hasattr(queryset.model, 'updated_at')):
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
            conflict_judge_last_name=F('judges__judge__last_name'),)

        if conflicting_sessions.exists():
            conflict = conflicting_sessions.first()
            e = (
                f"تداخل زمانی رخ داده است. داور {conflict.conflict_judge_first_name} {conflict.conflict_judge_last_name} در کلاس دیگری با شناسه ({conflict.id}) "
                f"در تاریخ {conflict.get_date_jalali} و بازه زمانی {conflict.start_time} تا {conflict.end_time} حضور دارد."
            )
            messages.error(self.request, f"خطا : {e}")
            raise ValidationError(
                f'❌ {e}'
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
                     then=Concat(F('supervisor1__first_name'), Value(' '), F('supervisor1__last_name'))),  # Concatenate first_name and last_name
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
                f'❌ {e}'
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
                f'❌ {e}'
            )
    def validate_not_duplicate_judges_at_sameSession(self, judges):
        if len(judges) != len(set(judges)):
            e = (
                f"داوران در یک نشست نمیتوانند تکراری باشند"
            )
            messages.error(self.request, f"خطا : {e}")
            raise ValidationError(
                f'❌ {e}'
            )
    def validate_not_duplicate_professors_and_judges_atSameSession(self, judges):
        # Validate against supervisors and graduate_monitor in the parent form
        parent_session = self.instance  # Parent `Session` instance
        for judge in judges:
            if judge in [
                parent_session.supervisor1,
                parent_session.supervisor2,
                parent_session.supervisor3,
                parent_session.supervisor4,
                parent_session.graduate_monitor,
            ]:
                e = (f"داور {judge} نمی‌تواند یکی از اساتید یا ناظر در همین نشست باشد.")
                messages.error(self.request, f"خطا : {e}")
                raise ValidationError(
                    f'❌ {e}'
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
        formset = super(JudgeAssignmentInline, self).get_formset(request,obj,**kwargs)
        formset.request = request
        return formset


class SessionAdminForm(forms.ModelForm):
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
        try:
            # Call the model's clean method
            self.instance.clean()
        except ValidationError as e:
            # Raise form-level validation errors
            messages.error(self.request, e.message)
            raise forms.ValidationError(e.messages)

        return cleaned_data


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

    def get_form(self, request, *args, **kwargs):
        form = super(SessionAdmin, self).get_form(request, *args, **kwargs)
        form.request = request  # Pass the request object to the form
        return form

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
        try:
            obj.clean()  # Call the custom clean method before saving
        except ValidationError as e:
            # Catch the validation error and display it
            messages.error(request, str(e))
            self.message_user(request, str(e), level='error')
            return  # Don't save the model if validation fails
        super().save_model(request, obj, form, change)  # Save if no error

# Register the Session model with the custom admin class
admin.site.register(Session, SessionAdmin)
