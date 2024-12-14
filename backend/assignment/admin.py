from django.contrib import admin
from jalali_date import datetime2jalali

from .models import Session
from django.utils.translation import gettext_lazy as _


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
                supervisor3__isnull=True,
                supervisor4__isnull=False,
            )
        elif self.value() == '1':
            return queryset.filter(
                supervisor3__isnull=False,
                supervisor4__isnull=True,
            )
        elif self.value() == '2':
            return queryset.filter(
                supervisor3__isnull=False,
                supervisor4__isnull=False,
            )
        return queryset

class SessionAdmin(admin.ModelAdmin):
    # Fields to be displayed in the list view
    list_display = ('title', 'student', 'schedule', 'supervisor1', 'supervisor2', 'supervisor3', 'supervisor4', 'graduate_monitor', 'session_status', 'get_created_at_jalali', 'get_updated_at_jalali')

    # Fields to be used for searching in the admin interface
    search_fields = ('title', 'student__user__first_name', 'student__user__last_name', 'supervisor1__user__first_name', 'supervisor1__user__last_name', 'supervisor2__user__first_name', 'supervisor2__user__last_name', 'supervisor3__user__first_name', 'supervisor3__user__last_name', 'supervisor4__user__first_name', 'supervisor4__user__last_name')

    # Filters to narrow down results in the list view
    list_filter = ('session_status', MonthFilter, MonthFilter_created_at,
                   MonthFilter_updated_at,
                   SupervisorCountFilter,
                   Consultant_ProfessorCountFilter)

    # Make sure the fields are read-only in certain cases, or configure which ones can be modified
    readonly_fields = ('get_created_at_jalali', 'get_updated_at_jalali')

    # Fieldsets to group fields logically in the form view
    fieldsets = (
        (_('A'), {
            'fields': ('title', 'description',)
        }),
        (_('B'), {
            'fields': ('schedule',)
        }),
        (_('C'), {
            'fields': ('student', 'supervisor1', 'supervisor2', 'supervisor3', 'supervisor4', 'graduate_monitor', 'session_status')
        }),
        (_('D'), {
            'fields': ('get_created_at_jalali',
                       'get_updated_at_jalali',
                       )
        }),
    )

    def get_fieldsets(self, request, obj=None):
        # If `obj` is None, it's the Add view
        if obj is None:
            # Exclude the "سایر اطلاعات" fieldset
            return (
                (_('A'), {
                    'fields': ('title', 'description',)
                }),
                (_('B'), {
                    'fields': ('schedule',)
                }),
                (_('C'), {
                    'fields': (
                    'student', 'supervisor1', 'supervisor2', 'supervisor3', 'supervisor4', 'graduate_monitor',
                    'session_status')
                }),
            )
        # Show all fieldsets (default) in the Change view
        return super().get_fieldsets(request, obj)

    # Prepopulate fields if needed (for example, auto-filling some fields)
    # prepopulated_fields = {'description': ('title',)}


    def get_readonly_fields(self, request, obj=None):
        # If `obj` is None, it's the "Add" view; otherwise, it's the "Change" view
        if obj is None:
            # Return an empty list of readonly fields in the Add view
            return []
        return self.readonly_fields

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

    # Custom form validation for saving the object
    def save_model(self, request, obj, form, change):
        # You can perform any custom save logic here
        super().save_model(request, obj, form, change)

# Register the Session model with the custom admin class
admin.site.register(Session, SessionAdmin)
