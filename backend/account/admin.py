from django.contrib import admin
from jalali_date import datetime2jalali
from jalali_date.admin import ModelAdminJalaliMixin

from .models import User
from django.utils.translation import gettext_lazy as _

class MonthFilter(ModelAdminJalaliMixin, admin.SimpleListFilter):
    title = _('آخرین ورود به سیستم')
    parameter_name = 'month'

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
            last_login_dates = queryset.values_list('uuid', 'last_login')

            # Filter using datetime2jalali without looping over queryset directly
            matching_ids = [
                uuid for uuid, last_login in last_login_dates
                if last_login and datetime2jalali(last_login).month == jalali_month
            ]

            return queryset.filter(uuid__in=matching_ids)  # Filter efficiently

        return queryset  # If no filter is applied, return the original queryset

from django.contrib.auth.admin import UserAdmin

@admin.register(User)
class UserAdmin(UserAdmin):

    # Display columns in the list view
    list_display = ['username', 'email', 'first_name', 'last_name',
                    'role',
                    'get_last_login_jalali',
                    'is_active', 'is_staff',
                    'verify_account',
                    'get_date_joined_jalali',]

    # Filters available in the list view
    list_filter = ['is_active', 'is_staff', 'verify_account',
                   'failed_login_attempts', 'date_joined',
                   MonthFilter, 'role']

    # Search fields for searching the list view
    search_fields = ['username', 'email', 'first_name', 'last_name']

    # Read-only fields in the form view
    readonly_fields = ['get_last_login_jalali',
                       'failed_login_attempts',
                       'last_login_ip',
                       'password_reset_attempts',
                       'get_last_failed_login_jalali',
                       'get_last_password_reset_jalali']

    # Fieldsets to group fields logically in the form view
    fieldsets = (
        (_('Info'), {
            'fields': ('username', 'email', 'first_name', 'last_name',),
        }),
        (_('Contact'), {
            'fields': ('phone_number',)
        }),
        (_('Permisions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'verify_account')
        }),
        (_('Details'), {
            'fields': ('failed_login_attempts',
                       'get_last_failed_login_jalali',
                       'get_last_login_jalali',
                       'password_reset_attempts',
                       'get_last_password_reset_jalali',
                       'last_login_ip',
                       )
        }),
        (_('Groups and Permissions'), {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',),  # Optional: Adds a collapsible section in the admin
            'description': _('Manage the groups and permissions for this user.'),  # Optional: Adds a description
        }),
    )

    # Ordering of the list view
    ordering = ['-date_joined']  # Orders by the most recent users

    # Actions for batch processing
    actions = ['reset_failed_login_attempts', 'lock_user_account']

    def get_readonly_fields(self, request, obj=None):
        # If `obj` is None, it's the "Add" view; otherwise, it's the "Change" view
        if obj is None:
            # Return an empty list of readonly fields in the Add view
            return []
        return self.readonly_fields

    def get_fieldsets(self, request, obj=None):
        # If `obj` is None, it's the Add view
        if obj is None:
            # Exclude the "سایر اطلاعات" fieldset
            return (
                ('Info', {
                    'fields': ('first_name', 'last_name', 'username', 'phone_number', 'email')
                }),
                (_('Permisions'), {
                    'fields': ('is_active', 'is_staff', 'is_superuser', 'verify_account')
                }),
                (_('Groups and Permissions'), {
                    'fields': ('groups', 'user_permissions'),
                    'classes': ('collapse',),  # Optional: Adds a collapsible section in the admin
                    'description': _('Manage the groups and permissions for this user.'),
                }),
            )
        # Show all fieldsets (default) in the Change view
        return super().get_fieldsets(request, obj)

    # Custom action to reset failed login attempts
    def reset_failed_login_attempts(self, request, queryset):
        updated_count = queryset.update(failed_login_attempts=0)
        self.message_user(request, f'{updated_count} user(s) had their failed login attempts reset.')

    reset_failed_login_attempts.short_description = _('ریست کردن تعداد لاگین های ناموفق برای کاربران انتخاب شده')

    # Custom action to lock the user account (e.g., if too many failed attempts)

    def lock_user_account(self, request, queryset):
        updated_count = queryset.update(is_active=False)
        self.message_user(request, f'{updated_count} user(s) have been locked due to too many failed login attempts.')

    lock_user_account.short_description = _('قفل حساب کاربری برای کاربران انتخاب شده')

    # Additional custom methods to display in list view
    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     # Example: Show only users who are not locked out
    #     return queryset.filter(is_active=True)

    @admin.display(description='تاریخ عضویت', ordering='date_joined')
    def get_date_joined_jalali(self, obj):
        if obj.date_joined:
            return datetime2jalali(obj.date_joined).strftime('%a, %d %b %Y | %H:%M:%S')
        else:
            return "ثبت نشده است"

    @admin.display(description='آخرین ورود به سیستم', ordering='last_login')
    def get_last_login_jalali(self, obj):
        if obj.last_login:
            return datetime2jalali(obj.last_login).strftime('%a, %d %b %Y | %H:%M:%S')
        else:
            return "ثبت نشده است"

    @admin.display(description='آخرین تلاش ناموفق', ordering='last_failed_login')
    def get_last_failed_login_jalali(self, obj):
        if obj.last_failed_login:
            return datetime2jalali(obj.last_failed_login).strftime('%a, %d %b %Y | %H:%M:%S')
        else:
            return "ثبت نشده است"

    @admin.display(description='آخرین بازنشانی رمز عبور', ordering='last_password_reset')
    def get_last_password_reset_jalali(self, obj):
        if obj.last_password_reset:
            return datetime2jalali(obj.last_password_reset).strftime('%a, %d %b %Y | %H:%M:%S')
        else:
            return "ثبت نشده است"
