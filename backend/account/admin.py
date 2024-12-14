from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from jalali_date import datetime2jalali
from .models import User, Group, GroupManager, Student, Teacher
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
        (_('Info'), {
            'fields': ('username', 'email', 'first_name', 'last_name',)
        }),
        (_('Permisions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser' ,'verify_account')
        }),
        (_('Contact'), {
            'fields': ('phone_number', 'address')
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
                    'fields': ('username', 'email', 'first_name', 'last_name',)
                }),
                (_('Permisions'), {
                    'fields': ('is_active', 'is_staff', 'is_superuser', 'verify_account')
                }),
                (_('Contact'), {
                    'fields': ('phone_number', 'address')
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



@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'field_of_study', 'role',
                    'get_created_at_jalali', 'get_updated_at_jalali')
    search_fields = ('name', 'field_of_study', 'role')
    list_filter = ('field_of_study', 'role', 'created_at', 'updated_at')
    ordering = ('name',)

    # Read-only fields in the form view
    readonly_fields = ['get_created_at_jalali',
                       'get_updated_at_jalali']

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

    def get_readonly_fields(self, request, obj=None):
        # If `obj` is None, it's the "Add" view; otherwise, it's the "Change" view
        if obj is None:
            # Return an empty list of readonly fields in the Add view
            return []
        return self.readonly_fields

@admin.register(GroupManager)
class GroupManagerAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'user_national_code', 'group',
                    'get_created_at_jalali', 'get_updated_at_jalali', 'edit_groupManger', 'edit_user')
    search_fields = ('user_full_name', 'group__name', 'user__email')
    list_filter = ('group', 'created_at', 'updated_at')

    # Read-only fields in the form view
    readonly_fields = ['get_created_at_jalali',
                       'get_updated_at_jalali']

    def user_full_name(self, obj):
        return f"{obj.professor.user.name}"
    user_full_name.short_description = "نام و نام خانوادگی"

    def user_national_code(self, obj):
        return f"{obj.professor.national_code}"
    user_national_code.short_description = "کد ملی"

    def edit_groupManger(self, obj):
        return format_html('<a href="{}">ویرایش مدیر گروه</a>', f"/admin/account/groupmanager/{obj.id}/change/")
    edit_groupManger.short_description = "ورود به پنل ویرایش مدیر گروه"

    def edit_user(self, obj):
        return format_html('<a href="{}">ویرایش کاربر</a>', f"/admin/account/user/{obj.professor.user.uuid}/change/")
    edit_user.short_description = "ورود به پنل ویرایش کاربر"

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

    def get_list_display_links(self, request, list_display):
        # Remove links from all columns
        return ('edit_teacher', 'edit_user')  # Keep the link only on `edit_teacher`

    def get_readonly_fields(self, request, obj=None):
        # If `obj` is None, it's the "Add" view; otherwise, it's the "Change" view
        if obj is None:
            # Return an empty list of readonly fields in the Add view
            return []
        return self.readonly_fields


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_number', 'user', 'role', 'status',
                    'lessons_group', 'get_created_at_jalali', 'get_updated_at_jalali')
    search_fields = ('student_number', 'user__email', 'user__first_name', 'user__last_name')
    list_filter = ('role', 'status', 'lessons_group', 'created_at', 'updated_at')
    ordering = ('student_number',)

    # Read-only fields in the form view
    readonly_fields = ['get_created_at_jalali',
                       'get_updated_at_jalali']

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

    def save_model(self, request, obj, form, change):
        # Check if the user is assigned as a teacher
        if hasattr(obj.user, 'teacher_profile'):
            self.message_user(
                request,
                _("این کاربر به عنوان استاد تعیین شده است و نمی‌توانید او را به عنوان یک دانشجو ثبت کنید."),
                level='error'
            )
            return
        super().save_model(request, obj, form, change)



@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'national_code',
                    'get_created_at_jalali', 'get_updated_at_jalali', 'edit_teacher', 'edit_user')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'national_code')
    list_filter = ('created_at', 'updated_at')
    ordering = ('user__first_name',)

    # Read-only fields in the form view
    readonly_fields = ['get_created_at_jalali',
                       'get_updated_at_jalali']

    def user_full_name(self, obj):
        return f"{obj.user.name}"
    user_full_name.short_description = "نام و نام خانوادگی"

    def edit_teacher(self, obj):
        return format_html('<a href="{}">ویرایش استاد</a>', f"/admin/account/teacher/{obj.id}/change/")
    edit_teacher.short_description = "ورود به پنل ویرایش استاد"

    def edit_user(self, obj):
        return format_html('<a href="{}">ویرایش کاربر</a>', f"/admin/account/user/{obj.user.uuid}/change/")
    edit_user.short_description = "ورود به پنل ویرایش کاربر"

    def get_list_display_links(self, request, list_display):
        # Remove links from all columns
        return ('edit_teacher', 'edit_user')  # Keep the link only on `edit_teacher`

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

    def save_model(self, request, obj, form, change):
        # Check if the user is assigned as a teacher
        if hasattr(obj.user, 'student_profile'):
            self.message_user(
                request,
                _("این کاربر به عنوان دانشجو تعیین شده است و نمی‌توانید او را به عنوان یک استاد ثبت کنید."),
                level='error'
            )
            return
        super().save_model(request, obj, form, change)