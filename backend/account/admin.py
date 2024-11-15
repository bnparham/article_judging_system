from django.contrib import admin
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
                    'last_login', 'last_login_ip',
                    'failed_login_attempts', 'is_active', 'is_staff', 'verify_account', 'date_joined']

    # Filters available in the list view
    list_filter = ['is_active', 'is_staff', 'verify_account', 'failed_login_attempts', 'date_joined', MonthFilter]

    # Search fields for searching the list view
    search_fields = ['username', 'email', 'first_name', 'last_name']

    # Read-only fields in the form view
    readonly_fields = ['last_login', 'last_login_ip', 'failed_login_attempts', 'last_failed_login']

    # Fields to display in the form view
    fields = ['username', 'email', 'first_name', 'last_name', 'password', 'is_active', 'is_staff',
              'verify_account', 'phone_number', 'address', 'profile_image', 'last_login', 'last_failed_login',
              'failed_login_attempts', 'last_login_ip', 'date_joined']

    # Fieldsets to group fields logically in the form view
    fieldsets = (
        (None, {
            'فیلذ ها': ('username', 'email', 'first_name', 'last_name', 'password',)
        }),
        (_('دسترسی ها'), {
            'fields': ('is_active', 'is_staff', 'verify_account')
        }),
        (_('اطلاعات تماس'), {
            'fields': ('phone_number', 'address')
        }),
        (_('سایر اطلاعات'), {
            'fields': ('failed_login_attempts', 'last_failed_login', 'last_login', 'last_login_ip',)
        }),
    )

    # Ordering of the list view
    ordering = ['-date_joined']  # Orders by the most recent users

    # Actions for batch processing
    actions = ['reset_failed_login_attempts', 'lock_user_account']

    # Custom action to reset failed login attempts
    def reset_failed_login_attempts(self, request, queryset):
        updated_count = queryset.update(failed_login_attempts=0)
        self.message_user(request, f'{updated_count} user(s) had their failed login attempts reset.')

    reset_failed_login_attempts.short_description = _('Reset Failed Login Attempts')

    # Custom action to lock the user account (e.g., if too many failed attempts)
    def lock_user_account(self, request, queryset):
        updated_count = queryset.update(is_active=False)
        self.message_user(request, f'{updated_count} user(s) have been locked due to too many failed login attempts.')

    lock_user_account.short_description = _('Lock User Account')

    # Additional custom methods to display in list view
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Example: Show only users who are not locked out
        return queryset.filter(is_active=True)

