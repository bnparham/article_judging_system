from django.core.exceptions import ValidationError
from django.db import models

class Session(models.Model):
    title = models.CharField(
        max_length=255,
        help_text="عنوان نشست را وارد کنید",
        verbose_name="عنوان نشست"
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="توضیحات نشست را وارد کنید (اختیاری)",
        verbose_name="نشست"
    )

    schedule = models.ForeignKey(
        'schedule.Schedule',  # Assuming you have a Schedule model in the schedule module
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name="زمانبندی",
        help_text="انتخاب برنامه تعریف شده از بخش داشبورد زمانبدی"
    )

    student = models.ForeignKey(
        'account.Student',
        on_delete=models.CASCADE,
        related_name="student_assignments",
        verbose_name="دانشجو",
        help_text="دانشجو را انتخاب کنید"
    )

    supervisor1 = models.ForeignKey(
        'account.Teacher',
        on_delete=models.CASCADE,
        related_name="supervisor1_assignments",
        verbose_name="استاد راهنما اول",
        help_text="استاد راهنمای اول را انتخاب کنید (اجباری)"
    )

    supervisor2 = models.ForeignKey(
        'account.Teacher',
        on_delete=models.CASCADE,
        related_name="supervisor2_assignments",
        verbose_name="استاد راهنما دوم",
        blank=True,
        null=True,
        help_text="استاد راهنمای دوم را انتخاب کنید (انتخاب اختیاری)"
    )

    supervisor3 = models.ForeignKey(
        'account.Teacher',
        on_delete=models.CASCADE,
        related_name="supervisor3_assignments",
        verbose_name="استاد مشاور اول",
        blank=True,
        null=True,
        help_text="استاد مشاور اول را انتخاب کنید (انتخاب اختیاری)"
    )

    supervisor4 = models.ForeignKey(
        'account.Teacher',
        on_delete=models.CASCADE,
        related_name="supervisor4_assignments",
        verbose_name="استاد مشاور دوم",
        blank=True,
        null=True,
        help_text="استاد مشاور دوم را انتخاب کنید (انتخاب اختیاری)"
    )

    graduate_monitor = models.ForeignKey(
        'account.Teacher',
        on_delete=models.CASCADE,
        related_name="graduate_monitor_assignments",
        verbose_name="ناظر تحصیلات تکمیلی",
        help_text="ناظر تحصیلات تکمیلی را انتخاب کنید (اجباری)"
    )

    # Optional: A date when the assignment should be completed or submitted
    session_status = models.BooleanField(
        default=True,
        help_text="آیا این نشست به اتمام رسیده یا خیر",
        verbose_name="بررسی وضعیت نشست"
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

    class Meta:
        verbose_name = 'نشست'
        verbose_name_plural = 'نشست ها'

    def clean(self):
        # Check if the student is already assigned to another session with the same schedule
        conflicting_student = Session.objects.filter(student=self.student, schedule=self.schedule)
        if conflicting_student.exists():
            raise ValidationError(f"Student {self.student} is already assigned to a session with this schedule.")

        # Check if supervisor1 is already assigned to another session with the same schedule
        if self.supervisor1:
            conflicting_supervisor1 = Session.objects.filter(supervisor1=self.supervisor1, schedule=self.schedule)
            if conflicting_supervisor1.exists():
                raise ValidationError(f"Supervisor {self.supervisor1} is already assigned to a session with this schedule.")

        # Check if supervisor2 is already assigned to another session with the same schedule
        if self.supervisor2:
            conflicting_supervisor2 = Session.objects.filter(supervisor2=self.supervisor2, schedule=self.schedule)
            if conflicting_supervisor2.exists():
                raise ValidationError(f"Supervisor {self.supervisor2} is already assigned to a session with this schedule.")

        # Check if supervisor3 is already assigned to another session with the same schedule
        if self.supervisor3:
            conflicting_supervisor3 = Session.objects.filter(supervisor3=self.supervisor3, schedule=self.schedule)
            if conflicting_supervisor3.exists():
                raise ValidationError(f"Supervisor {self.supervisor3} is already assigned to a session with this schedule.")

        # Check if supervisor4 is already assigned to another session with the same schedule
        if self.supervisor4:
            conflicting_supervisor4 = Session.objects.filter(supervisor4=self.supervisor4, schedule=self.schedule)
            if conflicting_supervisor4.exists():
                raise ValidationError(f"Supervisor {self.supervisor4} is already assigned to a session with this schedule.")

        # Check if the graduate monitor is already assigned to another session with the same schedule
        if self.graduate_monitor:
            conflicting_graduate_monitor = Session.objects.filter(graduate_monitor=self.graduate_monitor, schedule=self.schedule)
            if conflicting_graduate_monitor.exists():
                raise ValidationError(f"Graduate Monitor {self.graduate_monitor} is already assigned to a session with this schedule.")