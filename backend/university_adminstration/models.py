from django.db import models
from django.utils.translation import gettext_lazy as _
from .validators import is_persian_only, validate_email_domain, validate_iranian_mobile_number

class FacultyEducationalGroup(models.Model):
    # Define Faculties
    FACULTY_CHOICES_DICT = {
        'HUM': 'دانشکده ادبیات و علوم انسانی',  # Faculty of Literature and Humanities
        'PHY': 'دانشکده تربیت بدنی و علوم ورزشی',  # Faculty of Physical Education and Sports Sciences
        'BAS': 'دانشکده علوم پایه',  # Faculty of Basic Sciences
        'MAT': 'دانشکده علوم ریاضی',  # Faculty of Mathematical Sciences
        'MAR': 'دانشکده علوم و فنون دریایی',  # Faculty of Marine Sciences and Technology
        'CHE': 'دانشکده شیمی',  # Faculty of Chemistry
        'AGR': 'دانشکده علوم کشاورزی',  # Faculty of Agricultural Sciences
        'ENGE': 'دانشکده فنی و مهندسی شرق گیلان',  # Faculty of Engineering and East Gilan Technology
        'ENG': 'دانشکده فنی',  # Faculty of Engineering
        'MNG': 'دانشکده مدیریت و اقتصاد',  # Faculty of Management and Economics
        'ARC': 'دانشکده معماری و هنر',  # Faculty of Architecture and Art
        'NAT': 'دانشکده منابع طبیعی',  # Faculty of Natural Resources
        'MECH': 'دانشکده مهندسی مکانیک',  # Faculty of Mechanical Engineering
        'UNI': 'پردیس دانشگاهی',  # University Campus
        'CAS': 'پژوهشکده حوزه دریای کاسپین',  # Caspian Sea Research Institute
        'GIL': 'پژوهشکده گیلان شناسی',  # Gilan Studies Research Institute
    }

    faculty = models.CharField(
        max_length=5,
        choices=FACULTY_CHOICES_DICT.items(),
        verbose_name='دانشکده',
        default='MAT',
    )

    # Define Educational Groups Related to Each Faculty
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
    }


    educational_group = models.CharField(
        max_length=10,
        choices=[(_, label) for groups in EDUCATIONAL_GROUP_CHOICES.values() for _, label in groups],
        verbose_name="گروه آموزشی",
        default='MAT',
    )

    def save(self, *args, **kwargs):
        """ Ensure that the selected educational group belongs to the selected faculty """
        valid_choices = dict(self.EDUCATIONAL_GROUP_CHOICES).get(self.faculty, [])
        valid_group_keys = [key for key, _ in valid_choices]
        if self.educational_group not in valid_group_keys:
            self.educational_group = None  # Reset if invalid choice
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_faculty_display()} - {self.get_educational_group_display()}"

    class Meta:
        verbose_name = "دانشکده و گروه آموزشی"
        verbose_name_plural = "دانشکده‌ها و گروه‌های آموزشی"
        constraints = [
            models.UniqueConstraint(fields=['faculty', 'educational_group'], name='unique_faculty_educationalGroup',)]

class Student(models.Model):
    ROLES_DICT = {
        'Ph.D.': 'دکتری',
        'Master': 'ارشد',
    }
    SERVICE_STATUS_CHOICES = [
        ('Subject', 'مشمول'),  # Obligated for service but not yet started
        ('NotSubject', 'غیر مشمول'),  # Not obligated for service
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
        null=False,
        blank=False,
        editable=False
    )
    military_status = models.CharField(
        max_length=20,
        verbose_name='وضعیت سربازی',
        choices=SERVICE_STATUS_CHOICES,
        null=False,
        blank=False,
        editable=True,
    )
    program_type = models.CharField(
        max_length=10,
        verbose_name='دوره',
        choices=PROGRAM_TYPE_CHOICES,
        null=False,
        blank=False,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="ساخته شده در زمان/تاریخ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش در زمان/تاریخ")
    faculty_educational_group = models.ForeignKey(
        'FacultyEducationalGroup',
        on_delete=models.CASCADE,
        related_name='student_FEG',
        verbose_name="دانشکده و گروه آموزشی",
        help_text="دانشکده و گروه آموزشی ای که دانشجو به آن تخصیص داده میشود",
        null=False,
        blank=False,
        editable=False,
    )

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

class TeacherFacultyEducationalGroupAssignment(models.Model):
    faculty_educational_group = models.ForeignKey(
        'FacultyEducationalGroup',
        on_delete=models.CASCADE,
        related_name='teacher_FEG',
        verbose_name="دانشکده و گروه آموزشی",
        help_text="دانشکده و گروه آموزشی ای که استاد به آن تخصیص داده میشود"
    )
    teacher = models.ForeignKey(
        'university_adminstration.Teacher',
        on_delete=models.CASCADE,
        verbose_name="استاد",
    )

    def __str__(self):
        return f"{self.faculty_educational_group} - {self.teacher}"