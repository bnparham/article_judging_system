from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Case, When, F, Value, CharField
from django.db.models.functions import Concat
from jalali_date import date2jalali

class Session(models.Model):

    CLASS_CHOICES = [
        ('1', 'کلاس شماره 1'),
        ('2', 'کلاس شماره 2'),
        ('3', 'کلاس شماره 3'),
        ('4', 'کلاس شماره 4'),
        ('5', 'کلاس شماره 5'),
        ('6', 'کلاس شماره 6'),
        ('7', 'کلاس شماره 7'),
        ('8', 'کلاس شماره 8'),
    ]

    description = models.TextField(
        blank=True,
        null=True,
        help_text="توضیحات پیرامون نشست را وارد کنید (اختیاری)",
        verbose_name="توضیحات جلسه"
    )

    schedule = models.ForeignKey(
        'schedule.Schedule',  # Assuming you have a Schedule model in the schedule module
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name="زمانبندی",
        help_text="انتخاب برنامه تعریف شده از بخش داشبورد زمانبدی"
    )

    date = models.DateField(
        help_text="تاریخ برنامه",
        verbose_name='تاریخ',
    )
    start_time = models.TimeField(
        help_text="زمان شروع را تعیین کنید",
        verbose_name='زمان شروع'
    )
    end_time = models.TimeField(
        help_text="زمان پایان را تعیین کنید",
        verbose_name='زمان پایان'
    )

    class_number = models.CharField(
        max_length=1,
        choices=CLASS_CHOICES,
        verbose_name="کلاس",
        help_text="انتخاب کلاس",
        default=CLASS_CHOICES[0],
    )

    student = models.ForeignKey(
        'university_adminstration.Student',
        on_delete=models.CASCADE,
        related_name="student_assignments",
        verbose_name="دانشجو",
        help_text="دانشجو را انتخاب کنید"
    )

    supervisor1 = models.ForeignKey(
        'university_adminstration.Teacher',
        on_delete=models.CASCADE,
        related_name="supervisor1_assignments",
        verbose_name="استاد راهنما اول",
        help_text="استاد راهنمای اول را انتخاب کنید (اجباری)"
    )

    supervisor2 = models.ForeignKey(
        'university_adminstration.Teacher',
        on_delete=models.CASCADE,
        related_name="supervisor2_assignments",
        verbose_name="استاد راهنما دوم",
        blank=True,
        null=True,
        help_text="استاد راهنمای دوم را انتخاب کنید (انتخاب اختیاری)"
    )

    supervisor3 = models.ForeignKey(
        'university_adminstration.Teacher',
        on_delete=models.CASCADE,
        related_name="supervisor3_assignments",
        verbose_name="استاد مشاور اول",
        blank=True,
        null=True,
        help_text="استاد مشاور اول را انتخاب کنید (انتخاب اختیاری)"
    )

    supervisor4 = models.ForeignKey(
        'university_adminstration.Teacher',
        on_delete=models.CASCADE,
        related_name="supervisor4_assignments",
        verbose_name="استاد مشاور دوم",
        blank=True,
        null=True,
        help_text="استاد مشاور دوم را انتخاب کنید (انتخاب اختیاری)"
    )

    graduate_monitor = models.ForeignKey(
        'university_adminstration.Teacher',
        on_delete=models.CASCADE,
        related_name="graduate_monitor_assignments",
        verbose_name="ناظر تحصیلات تکمیلی",
        help_text="ناظر تحصیلات تکمیلی را انتخاب کنید (اجباری)"
    )

    is_active = models.BooleanField(
        default=False,
        editable=False,
        verbose_name="آیا این جلسه قابل برگزاری هست یا خیر",
        help_text="چناچه داور یا داوران به این نشست تخصیص داده نشود این نشست قابل برگزاری نخواهد بود"
    )

    # Optional: A date when the assignment should be completed or submitted
    session_status = models.BooleanField(
        default=False,
        help_text="آیا این نشست به اتمام رسیده یا خیر",
        verbose_name="وضعیت اتمام نشست"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="زمان ایجاد نشست",
        verbose_name="ساخته شده در زمان"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="زمان آخرین به‌روزرسانی نشست",
        verbose_name="آخرین ویرایش در زمان"
    )

    created_by = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="کاربری که نشست را ایجاد کرده است",
        verbose_name="ایجاد شده توسط"
    )

    updated_by = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="کاربری که آخرین بار نشست را به‌روزرسانی کرده است",
        verbose_name="ویرایش شده توسط"
    )

    faculty_educational_group = models.ForeignKey(
        'university_adminstration.FacultyEducationalGroup',
        on_delete=models.CASCADE,
        related_name='session_FEG',
        verbose_name="دانشکده و گروه آموزشی",
        help_text="دانشکده و گروه آموزشی ای که دانشجو به آن تخصیص داده میشود",
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = 'جلسه دفاع پایان نامه / رساله'
        verbose_name_plural = 'جلسات دفاع پایان نامه / رساله'
        constraints = [
            models.UniqueConstraint(fields=['schedule', 'date', 'class_number',
                                            'start_time', 'end_time', 'faculty_educational_group'],
                                    name='unique_session',)]

    @property
    def get_date_jalali(self):
        if self.date:
            return date2jalali(self.date).strftime('%a, %d %b %Y')
        else:
            return "ثبت نشده است"

    def __str__(self):
        show_id = f" جلسه دفاعیه با شناسه {self.id}"
        show_date = f'{self.schedule} / تاریخ :  {self.get_date_jalali} / ساعت برگزاری : {self.start_time} الی  {self.end_time}'
        show_person = f"{self.student}"
        return f"{show_id} | {show_person} | {show_date}"

class JudgeAssignment(models.Model):
    session = models.ForeignKey(
        'Session',
        on_delete=models.CASCADE,
        related_name='judges',
        verbose_name="نشست",
        help_text="نشستی که این داور به آن تخصیص داده می‌شود"
    )
    judge = models.ForeignKey(
        'university_adminstration.Teacher',
        on_delete=models.CASCADE,
        verbose_name="داور",
        help_text="داور تخصیص داده شده"
    )

    def __str__(self):
        return f"{self.session} - {self.judge}"
