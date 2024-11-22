from django.db import models

# Create your models here.
from django.db.models.functions import Now
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
import uuid
from django.contrib.auth.validators import UnicodeUsernameValidator
from .validators import is_persian_only
from django.conf import settings

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
    email = models.EmailField(unique=True, verbose_name='ایمیل', null=False, blank=False)
    phone_number = models.CharField(max_length=100, verbose_name='شماره موبایل', unique=True, null=False, blank=False)
    birthday = models.DateField(null=True, blank=True, verbose_name="تاریخ تولد")
    gender = models.CharField(
        max_length=1,
        choices=[('M', 'مرد'), ('F', 'زن'), ('O', 'سایر')],
        null=True,
        blank=True,
        verbose_name="جنسیت"
    )
    address = models.TextField(max_length=500, verbose_name="آدرس محل زندگی", default=None, null=True, blank=True)
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
        return self.email

    @classmethod
    def make_verify_user_account(cls, user):
        user = User.objects.get(uuid=user.uuid)
        user.verify_account = True
        user.save()
        return user

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

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='نام گروه') 
    field_of_study = models.CharField(max_length=100, verbose_name='رشته تحصیلی') 
    role = models.CharField(max_length=50)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class GroupManager(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="managed_groups"
    )  
    group = models.ForeignKey(
        'Group',
        on_delete=models.CASCADE,
        verbose_name='گروه',
        related_name="managers"
    )  
    name = models.CharField(max_length=150, verbose_name='نام مدیر گروه')  
    national_code = models.CharField(max_length=10, unique=True, verbose_name='کدملی')  

    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"{self.name} - {self.group.name}"

    class Meta:
        verbose_name = "مدیر گروه"
        verbose_name_plural = "لیست مدیر گروه ها"

class Student(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='students'
    )
    student_number = models.CharField(max_length=20, unique=True, verbose_name='شماره دانشجویی')
    lessons_group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='گروه',
        related_name='students_group'
    )
    role = models.CharField(max_length=50,verbose_name='مقطع تحصیلی', choices=[
        ('دکتری', 'Ph.D.'),
        ('ارشد', 'Master'),
    ])
    status = models.CharField(max_length=20, verbose_name='وضعیت', choices=[
        ('ترم جاری', 'Current'),
        ('دفاع شده', 'Defended'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student_number} - {self.user.get_full_name()} ({self.role})"

class Teacher(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile"
    )
    name = models.CharField(max_length=150, verbose_name='نام استاد')
    national_code = models.CharField(max_length=10, unique=True, verbose_name='کدملی')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "استاد"
        verbose_name_plural = "لیست اساتید"