from django.contrib import admin
from jalali_date import datetime2jalali
from .models import User
from django.utils.translation import gettext_lazy as _


class MonthFilter(admin.SimpleListFilter):
    title = _('ماه')
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
            if(hasattr(queryset.model, 'date_joined')):
                return queryset.filter(date_joined__month=self.value())
            elif(hasattr(queryset.model, 'expiry_date')):
                return queryset.filter(expiry_date__month=self.value())
            elif(hasattr(queryset.model, 'start_date')):
                return queryset.filter(start_date__month=self.value())


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    # Display columns in the list view
    list_display = ['username', 'email', 'first_name', 'last_name',
                    'get_last_login_jalali',
                    'is_active', 'is_staff', 'verify_account', 'get_date_joined_jalali']

    # Filters available in the list view
    list_filter = ['is_active', 'is_staff', 'verify_account', 'failed_login_attempts', 'date_joined', MonthFilter]

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
        (None, {
            'fields': ('username', 'email', 'first_name', 'last_name',)
        }),
        (_('دسترسی ها'), {
            'fields': ('is_active', 'is_staff', 'verify_account')
        }),
        (_('اطلاعات تماس'), {
            'fields': ('phone_number', 'address')
        }),
        (_('سایر اطلاعات'), {
            'fields': ('failed_login_attempts',
                       'get_last_failed_login_jalali',
                       'get_last_login_jalali',
                       'password_reset_attempts',
                       'get_last_password_reset_jalali',
                       'last_login_ip',
                       )
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
                (None, {
                    'fields': ('username', 'email', 'first_name', 'last_name',)
                }),
                (_('دسترسی ها'), {
                    'fields': ('is_active', 'is_staff', 'verify_account')
                }),
                (_('اطلاعات تماس'), {
                    'fields': ('phone_number', 'address')
                }),
            )
        # Show all fieldsets (default) in the Change view
        return super().get_fieldsets(request, obj)

    # Custom action to reset failed login attempts
    def reset_failed_login_attempts(self, request, queryset):
        updated_count = queryset.update(failed_login_attempts=0)
        self.message_user(request, f'{updated_count} user(s) had their failed login attempts reset.')

    reset_failed_login_attempts.short_description = _('ریست کردن تعداد لاگین های ناموفق برای کاربران انتختاب شده')

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
        if obj.date_joined :
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

