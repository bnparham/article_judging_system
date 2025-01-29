from django.db import models
from django.utils.translation import gettext_lazy as _
from .validators import is_persian_only, validate_email_domain, validate_iranian_mobile_number

class EducationalGroup(models.Model):
    FIELD_OF_STUDY_CHOICES_DICT = {
        'CS': 'کامپیوتر',  # Computer Science
        'MAT': 'ریاضی',  # Mathematics
        'STA': 'آمار'  # Statistics
    }

    ROLE_CHOICES_DICT = {
        'Ph.D.': 'دکتری',
        'Master': 'ارشد'
    }

    field_of_study = models.CharField(
        max_length=3,
        choices=FIELD_OF_STUDY_CHOICES_DICT,
        verbose_name='رشته تحصیلی'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES_DICT,
        verbose_name='گروه ارشد | دکتری'
    )

    def __str__(self):
        return f" گروه {self.FIELD_OF_STUDY_CHOICES_DICT[self.field_of_study]} - {self.ROLE_CHOICES_DICT[self.role]}"

    class Meta:
        verbose_name = "گروه های آموزشی"
        verbose_name_plural = "گروه های آموزشی تعریف شده در دانشکده"
        constraints = [
            models.UniqueConstraint(fields=['field_of_study', 'role'], name='unique_field_role',)]



class Student(models.Model):
    ROLES_DICT = {
        'Ph.D.': 'دکتری',
        'Master': 'ارشد',
    }
    SERVICE_STATUS_CHOICES = [
        ('Completed', 'پایان یافته'),
        ('Exempt', 'معاف'),
        ('Pending', 'در حال انجام'),
    ]
    PROGRAM_TYPE_CHOICES = [
        ('Day', 'روزانه'),
        ('Night', 'شبانه'),
        ('Campus', 'پردیس'),
    ]
    GENDER_CHOICES = [
        ('Male', 'مرد'),
        ('Female', 'زن'),
        ('Other', 'دیگر'),
    ]

    first_name = models.CharField(_("نام"), max_length=150, editable=False, blank=True)
    last_name = models.CharField(_("نام خانوادگی"), max_length=150, editable=False, blank=True)
    # TODO : add validator
    email = models.EmailField(unique=True,
                              verbose_name='ایمیل',
                              null=True,
                              blank=True,
                              validators=[validate_email_domain],
                              editable=False)
    # TODO : add validator
    phone_number = models.CharField(max_length=11,
                                    verbose_name='شماره موبایل',
                                    unique=True,
                                    null=False,
                                    blank=True,
                                    validators=[validate_iranian_mobile_number],
                                    editable=False
                                    )
    student_number = models.CharField(max_length=20, unique=True,
                                      verbose_name='شماره دانشجویی',
                                      editable=False)
    educational_group = models.ForeignKey(
        EducationalGroup,
        on_delete=models.PROTECT,
        verbose_name='گروه',
        related_name='students_group',
        editable=False,
        null=True,
    )
    role = models.CharField(max_length=20,
                            verbose_name='مقطع تحصیلی',
                            choices=ROLES_DICT,
                            editable=False)
    status = models.CharField(max_length=20,
                              verbose_name='وضعیت',
                              choices=[
                                    ('Current', 'دانشجو'),
                                    ('Defended', 'دانش آموخته'),
                                ],
                              editable=True)
    admission_year = models.PositiveIntegerField(
        verbose_name="سال ورود",
        default=0,
        editable=False
    )
    gender = models.CharField(
        max_length=10,
        verbose_name='جنسیت',
        choices=GENDER_CHOICES,
        null=True,
        blank=True,
        editable=False
    )
    military_status = models.CharField(
        max_length=20,
        verbose_name='وضعیت سربازی',
        choices=SERVICE_STATUS_CHOICES,
        null=True,
        blank=True,
        editable=True,
    )
    program_type = models.CharField(
        max_length=10,
        verbose_name='دوره',
        choices=PROGRAM_TYPE_CHOICES,
        null=True,
        blank=True,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="ساخته شده در زمان/تاریخ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش در زمان/تاریخ")

    def __str__(self):
        if self.gender == "Male":
            name = f'آقای {self.name} '
        elif self.gender == "Female":
            name = f'خانم {self.name}  '
        return f"{name}"

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = "دانشجو"
        verbose_name_plural = "لیست دانشجویان"

    def save(self, *args, **kwargs):
        if self.pk:  # Check if the object already exists in the database
            raise ValueError("Student object cannot be modified.")
        super().save(*args, **kwargs)

class Teacher(models.Model):
    first_name = models.CharField(_("نام"), max_length=150, blank=True)
    last_name = models.CharField(_("نام خانوادگی"), max_length=150, blank=True)
    # TODO : add validator
    email = models.EmailField(unique=True,
                              verbose_name='ایمیل',
                              null=False,
                              blank=False,
                              validators=[validate_email_domain], )
    # TODO : add validator
    phone_number = models.CharField(max_length=11,
                                    verbose_name='شماره موبایل',
                                    unique=True,
                                    null=False,
                                    blank=False,
                                    validators=[validate_iranian_mobile_number],
                                    )

    national_code = models.CharField(max_length=10, unique=True, verbose_name='کدملی')
    faculty_id = models.CharField(
                                 max_length=20,
                                 unique=True,
                                 verbose_name='کد استاد',
                                 )
    degree = models.CharField(max_length=20,
                              verbose_name='مدرک تحصیلی',
                              choices=[
                                  ('MASTER', 'کارشناسی ارشد'),  # Master's Degree
                                  ('PHD', 'دکتری')  # Doctorate (Ph.D.)
                              ])
    educational_groups = models.ManyToManyField(
        'EducationalGroup',
        related_name="teachers_group",
        verbose_name="گروه‌های آموزشی",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="ساخته شده در زمان/تاریخ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش در زمان/تاریخ")

    def __str__(self):
        return self.name

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = "استاد"
        verbose_name_plural = "لیست اساتید"