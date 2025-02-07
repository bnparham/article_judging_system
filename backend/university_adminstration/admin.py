from django.contrib import admin
from django import forms
from django.db.models import Q

from .models import Student, Teacher, FacultyEducationalGroup, TeacherFacultyEducationalGroupAssignment
from jalali_date import datetime2jalali
from django.utils.html import format_html

@admin.register(FacultyEducationalGroup)
class FacultyEducationalGroupAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'educational_group')
    list_filter = ('faculty',)
    search_fields = ('faculty', 'educational_group')

    class Media:
        js = ('admin/js/faculty_filter.js',)  # Load our custom JS file
    # Prevent deleting objects in the admin panel
    def has_delete_permission(self, request, obj=None):
        return False

    # Prevent chaning objects in the admin panel
    def has_change_permission(self, request, obj=None):
        return False

    def get_list_display_links(self, request, list_display):
        # Remove links from all columns
        return

    FACULTY_CHOICES_DICT = {
        'HUM': 'دانشکده ادبیات و علوم انسانی',
        'PHY': 'دانشکده تربیت بدنی و علوم ورزشی',
        'BAS': 'دانشکده علوم پایه',
        'MAT': 'دانشکده علوم ریاضی',
        'MAR': 'دانشکده علوم و فنون دریایی',
        'CHE': 'دانشکده شیمی',
        'AGR': 'دانشکده علوم کشاورزی',
        'ENGE': 'دانشکده فنی و مهندسی شرق گیلان',
        'ENG': 'دانشکده فنی',
        'MNG': 'دانشکده مدیریت و اقتصاد',
        'ARC': 'دانشکده معماری و هنر',
        'NAT': 'دانشکده منابع طبیعی',
        'MECH': 'دانشکده مهندسی مکانیک',
        'UNI': 'پردیس دانشگاهی',
        'CAS': 'پژوهشکده حوزه دریای کاسپین',
        'GIL': 'پژوهشکده گیلان شناسی',
    }
    EDUCATIONAL_GROUP_CHOICES = {
        'MAT': [
            ('APPMATH', 'ریاضیات کاربردی'),
            ('PUREMATH', 'ریاضیات محض'),
            ('STAT', 'آمار'),
            ('CS', 'علوم کامپیوتر'),
        ],
        'ENG': [
            ('ELEC', 'برق'),
            ('MECH', 'مکانیک'),
            ('CIVIL', 'عمران'),
        ],
        'CHE': [
            ('CHEM', 'شیمی کاربردی'),
            ('CHEMENG', 'مهندسی شیمی'),
        ],
        'MGT': [
            ('BUS', 'مدیریت بازرگانی'),
            ('ECON', 'اقتصاد'),
        ],
    }

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        # Partial search for faculty names
        faculty_matches = [k for k, v in self.FACULTY_CHOICES_DICT.items() if search_term in v]
        if faculty_matches:
            queryset |= self.model.objects.filter(Q(faculty__in=faculty_matches))

        # Partial search for educational groups
        edu_reverse_map = {k: v for sublist in self.EDUCATIONAL_GROUP_CHOICES.values() for k, v in sublist}
        edu_matches = [k for k, v in edu_reverse_map.items() if search_term in v]
        if edu_matches:
            queryset |= self.model.objects.filter(Q(educational_group__in=edu_matches))

        return queryset, use_distinct

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'student_number', 'email', 'phone_number', 'role',
                    'admission_year', 'gender',
                    'edit_student')
    search_fields = ('student_number', 'email', 'first_name', 'last_name', 'phone_number', 'admission_year')
    list_filter = ('role', 'status', 'military_status', 'program_type', 'gender')
    ordering = ('student_number',)

    # Read-only fields in the form view
    readonly_fields = (
        'first_name', 'last_name', 'email', 'phone_number',
        'student_number', 'role',
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
        return format_html('<a href="{}">مشاهده دانشجو</a>', f"/admin/university_adminstration/student/{obj.id}/change/")
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


class TeacherFacultyEducationalGroupAssignmentInline(admin.TabularInline):
    model = TeacherFacultyEducationalGroupAssignment
    extra = 1  # Number of empty rows to show for adding new judges
    verbose_name = "دانشکده و گروه آموزشی"
    verbose_name_plural = "تخصیص رشته"
    autocomplete_fields = ['faculty_educational_group']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('teacher', 'faculty_educational_group')  # Optimize related field

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(TeacherFacultyEducationalGroupAssignmentInline, self).get_formset(request, obj, **kwargs)
        formset.request = request
        return formset

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    inlines = [TeacherFacultyEducationalGroupAssignmentInline]
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
        return format_html('<a href="{}">ویرایش استاد</a>', f"/admin/university_adminstration/teacher/{obj.id}/change/")
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

