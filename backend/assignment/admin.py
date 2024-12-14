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

class SessionAdmin(admin.ModelAdmin):
    # Fields to be displayed in the list view
    list_display = ('title', 'student', 'schedule', 'supervisor1', 'supervisor2', 'supervisor3', 'supervisor4', 'graduate_monitor', 'session_status', 'get_created_at_jalali', 'get_updated_at_jalali')

    # Fields to be used for searching in the admin interface
    search_fields = ('title', 'student__user__first_name', 'student__user__last_name', 'supervisor1__user__first_name', 'supervisor1__user__last_name', 'supervisor2__user__first_name', 'supervisor2__user__last_name', 'supervisor3__user__first_name', 'supervisor3__user__last_name', 'supervisor4__user__first_name', 'supervisor4__user__last_name')

    # Filters to narrow down results in the list view
    list_filter = ('session_status', MonthFilter)

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
            'fields': ('student' ,'supervisor1', 'supervisor2', 'supervisor3', 'supervisor4', 'graduate_monitor', 'session_status')
        }),
        (_('D'), {
            'fields': ('get_created_at_jalali',
                       'get_updated_at_jalali',
                       )
        }),
    )

    # Prepopulate fields if needed (for example, auto-filling some fields)
    # prepopulated_fields = {'description': ('title',)}


    def get_readonly_fields(self, request, obj=None):
        # If `obj` is None, it's the "Add" view; otherwise, it's the "Change" view
        if obj is None:
            # Return an empty list of readonly fields in the Add view
            return []
        return self.readonly_fields

    @admin.display(description='ایجاد شده در زمان', ordering='created_at')
    def get_created_at_jalali(self, obj):
        if obj.created_at:
            return datetime2jalali(obj.created_at).strftime('%a, %d %b %Y | %H:%M:%S')
        else:
            return "ثبت نشده است"

    @admin.display(description='آخرین ویرایش در زمان', ordering='updated_at')
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
