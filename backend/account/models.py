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
    FACULTY_CHOICES_DICT = {
        'ALL': 'دسترسی به همه دانشکده ها',
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
    role = models.CharField(
        max_length=5,
        choices=FACULTY_CHOICES_DICT.items(),
        verbose_name='دانشکده',
        default='ALL',
        help_text="دانشکده ای که این کاربر در آن فعالیت میکند را انتخاب کنید",
    )

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
        return f" کاربر {self.first_name} {self.last_name}"

    @classmethod
    def make_verify_user_account(cls, user):
        user = User.objects.get(uuid=user.uuid)
        user.verify_account = True
        user.save()
        return user

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

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

    @property
    def user_info(self):
        value = ""
        match self.role:
            case 'ALL':
                value = "همه دانشکده ها"
            case _ :
                value = f"{self.FACULTY_CHOICES_DICT[self.role]}"
        return f" {self.name} " + "ℹ️" + f"  دسترسی به مدیریت {value} "

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


# change name of django defualt app names
auth_group._meta.verbose_name = "گروه کاربران"  # Singular name
auth_group._meta.verbose_name_plural = "گروه های کاربران"  # Plural name
