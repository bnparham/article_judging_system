from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.
from django.db.models.functions import Now
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
import uuid
from django.contrib.auth.validators import UnicodeUsernameValidator

from .validators import is_persian_only, validate_email_domain, validate_iranian_mobile_number
from django.conf import settings

from django.contrib.auth.models import Group as auth_group


class User(AbstractUser):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=150,
        unique=True,
        help_text=_(
            "مورد نیاز. 150 کاراکتر یا کمتر. فقط حروف، ارقام و @/./+/-/_."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("کاربری با این نام کاربری وجود دارد. لطفا نام کاربری دیگری انتخاب کنید"),
        },
        verbose_name='نام کاربری',
    )
    password = models.CharField(max_length=128, verbose_name='رمز عبور')
    first_name = models.CharField(max_length=150,
                                  blank=False,
                                  null=False,
                                  verbose_name='نام',
                                  validators=[is_persian_only])
    last_name = models.CharField(max_length=150,
                                 blank=False,
                                 null=False,
                                 verbose_name='نام خانوادگی',
                                 validators=[is_persian_only])
    is_staff = models.BooleanField(
        default=False,
        help_text=_("مشخص می کند که آیا کاربر می تواند به این سایت مدیریت وارد شود یا خیر."),
        verbose_name='دسترسی به پنل ادمین'
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_(
            "مشخص می کند که آیا این کاربر باید به عنوان کاربر فعال در نظر گرفته شود."
            "به جای حذف حساب‌ها، این مورد را لغو انتخاب کنید تا حساب کاربر غیرفعال شود."
        ),
        verbose_name='وضعیت فعال بودن/نبودن کاربر'
    )
    date_joined = models.DateTimeField(db_default=Now(), verbose_name='تاریخ عضویت')
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
    birthday = models.DateField(null=True, blank=True, verbose_name="تاریخ تولد")
    gender = models.CharField(
        max_length=1,
        choices=[('M', 'مرد'), ('F', 'زن'), ('O', 'سایر')],
        null=True,
        blank=True,
        verbose_name="جنسیت"
    )
    verify_account = models.BooleanField(default=False,
                                         verbose_name='تایید حساب کاربری',
                                         help_text="نشان میدهد کاربر شماره موبایل یا آدرس ایمیل خود را تایید کرده است یا خیر")
    password_reset_attempts = models.PositiveIntegerField(db_default=0, verbose_name="تعداد تلاش‌های بازنشانی رمز عبور")
    last_password_reset = models.DateTimeField(null=True, blank=True, verbose_name="آخرین بازنشانی رمز عبور")
    failed_login_attempts = models.PositiveIntegerField(db_default=0, verbose_name="تعداد تلاش‌های ورود ناموفق")
    last_failed_login = models.DateTimeField(null=True, blank=True, verbose_name="آخرین تلاش ناموفق")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="آخرین ورود به سیستم")
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="آخرین آدرس آی‌پی ورود")

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = [
        'password',
        'email',
        'phone_number'
    ]

    class Meta:
        verbose_name = _("کاربر")
        verbose_name_plural = _("لیست کاربران")

    def __str__(self):
        if hasattr(self, 'teacher_profile'):
            return f"{self.email} - تخصیص یافته به عنوان استاد "
        elif hasattr(self, 'student_profile'):
            return f"{self.email} - تخصیص یافته به عنوان دانشجو "
        else:
            return f"{self.email} - تخصیص نیافته "

    @classmethod
    def make_verify_user_account(cls, user):
        user = User.objects.get(uuid=user.uuid)
        user.verify_account = True
        user.save()
        return user

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    def deactivate(self):
        self.is_active = False
        self.save()

    def lock_account(self):
        self.is_locked = True
        self.save()

    def set_last_login_ip(self, ip):
        self.last_login_ip = ip
        self.save()

    def increment_reset_attempts(self):
        """Increments reset attempts counter."""
        self.password_reset_attempts += 1
        self.save()

    def reset_password(self, new_password):
        """Handles the password reset logic."""
        self.set_password(new_password)
        self.password_reset_attempts = 0
        self.last_password_reset = now()
        self.save()


class EducationalGroup(models.Model):
    FIELD_OF_STUDY_CHOICES = [
        ('CS', 'کامپیوتر'),  # Computer Science
        ('MAT', 'ریاضی'),  # Mathematics
        ('STA', 'آمار'),  # Statistics
    ]

    ROLE_CHOICES = [
        ('Ph.D.', 'دکتری'),
        ('Master', 'ارشد'),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name='نام گروه')
    field_of_study = models.CharField(
        max_length=3,
        choices=FIELD_OF_STUDY_CHOICES,
        verbose_name='رشته تحصیلی'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        verbose_name='گروه ارشد | دکتری'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="ساخته شده در زمان/تاریخ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش در زمان/تاریخ")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "گروه های آموزشی"
        verbose_name_plural = "گروه های آموزشی تعریف شده در دانشکده"


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
            name = f'{self.name} آقای '
        elif self.gender == "Female":
            name = f'{self.name} خانم '
        return f"| مقطع تحصیلی {self.ROLES_DICT[self.role]}{self.student_number} با شماره دانشجویی {name}"

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


# change name of django defualt app names
auth_group._meta.verbose_name = "گروه کاربران"  # Singular name
auth_group._meta.verbose_name_plural = "گروه های کاربران"  # Plural name
