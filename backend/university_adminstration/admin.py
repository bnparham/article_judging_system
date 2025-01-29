from django.contrib import admin

from .models import EducationalGroup, Student, Teacher
from jalali_date import datetime2jalali
from django.utils.html import format_html

@admin.register(EducationalGroup)
class EducationalGroupAdmin(admin.ModelAdmin):
    list_display = ('field_of_study', 'role', 'edit_educationl_group')
    search_fields = ('name', 'field_of_study', 'role')
    list_filter = ('field_of_study', 'role')

    # Prevent deleting objects in the admin panel
    def has_delete_permission(self, request, obj=None):
        return False

    # Prevent deleting objects in the admin panel
    def has_change_permission(self, request, obj=None):
        return False

    def edit_educationl_group(self, obj):
        return format_html('<a href="{}">مشاهده گروه</a>', f"/university_adminstration/educationalgroup/{obj.id}/change/")
    edit_educationl_group.short_description = "اطلاعات کامل گروه"

    def get_list_display_links(self, request, list_display):
        # Remove links from all columns
        return ('edit_educationl_group')  # Keep the link only on `edit_teacher`

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'student_number', 'email', 'phone_number', 'role',
                    'educational_group', 'admission_year', 'gender',
                    'edit_student')
    search_fields = ('student_number', 'email', 'first_name', 'last_name', 'phone_number', 'admission_year')
    list_filter = ('role', 'status', 'educational_group', 'military_status', 'program_type', 'gender')
    ordering = ('student_number',)

    # Read-only fields in the form view
    readonly_fields = (
        'first_name', 'last_name', 'email', 'phone_number',
        'student_number', 'educational_group', 'role',
        'admission_year', 'gender', 'military_status', 'program_type',
        'get_created_at_jalali',
        'get_updated_at_jalali'
    )

    def has_add_permission(self, request, obj=None):
        return False  # Always return False to disable adding new objects

    # Prevent deleting objects in the admin panel
    def has_delete_permission(self, request, obj=None):
        return False


    def user_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    user_full_name.short_description = "نام و نام خانوادگی"

    def edit_student(self, obj):
        return format_html('<a href="{}">مشاهده دانشجو</a>', f"/university_adminstration/student/{obj.id}/change/")
    edit_student.short_description = "اطلاعات کامل دانشجو"


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

    def get_list_display_links(self, request, list_display):
        # Remove links from all columns
        return ('edit_student')  # Keep the link only on `edit_teacher`

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'national_code',
                    'get_created_at_jalali', 'get_updated_at_jalali', 'edit_teacher')
    search_fields = ('first_name', 'last_name', 'email', 'national_code', 'faculty_id')
    list_filter = ('created_at', 'updated_at')
    ordering = ('first_name', 'last_name')

    # Read-only fields in the form view
    readonly_fields = ['get_created_at_jalali',
                       'get_updated_at_jalali']

    def user_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    user_full_name.short_description = "نام و نام خانوادگی"

    def edit_teacher(self, obj):
        return format_html('<a href="{}">ویرایش استاد</a>', f"/university_adminstration/teacher/{obj.id}/change/")
    edit_teacher.short_description = "ورود به پنل ویرایش استاد"

    def get_list_display_links(self, request, list_display):
        # Remove links from all columns
        return ('edit_teacher')  # Keep the link only on `edit_teacher`

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

