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
        default=False,
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
        # Check if the session is being created or updated
        is_updating = self.pk is not None

        # Check if the professor, supervisors, or graduate monitor are already assigned to another session at the same schedule
        conflicting_assignments = Session.objects.filter(
            schedule=self.schedule
        )

        if is_updating:
            # If updating, exclude the current session from the conflict check
            conflicting_assignments = conflicting_assignments.exclude(id=self.id)

        # Check for conflict with the student's previous sessions
        if conflicting_assignments.filter(student=self.student).exists():
            raise ValidationError(f"دانشجو {self.student}  در همین زمان در نشست دیگری حضور دارد ")

        # Check for conflict with supervisor1, supervisor2, supervisor3, supervisor4


        supervisors = [self.supervisor1, self.supervisor2, self.supervisor3, self.supervisor4]
        for supervisor in supervisors:
            # Check for conflict with graduate monitor with other supervisors
            GM_check = conflicting_assignments.filter(graduate_monitor=supervisor)
            print(GM_check)
            CA_1 = conflicting_assignments.filter(supervisor1=supervisor)
            if supervisor and GM_check.exists():
                raise ValidationError(
                    f"استاد {supervisor} به عنوان ناظر تحصیلات تکمیلی در همین زمان در نشست دیگری ({GM_check.last().title} - {GM_check.last().schedule}) حضور دارد ")
            if supervisor and CA_1.exists():
                raise ValidationError(
                    f"استاد {supervisor} به عنوان استاد راهنما اول در همین زمان در نشست دیگری ({CA_1.last().title} - {CA_1.last().schedule}) حضور دارد ")
            CA_2 = conflicting_assignments.filter(supervisor2=supervisor)
            if supervisor and CA_2.exists():
                raise ValidationError(
                    f"استاد {supervisor} به عنوان استاد راهنما دوم در همین زمان در نشست دیگری ({CA_2.last().title} - {CA_2.last().schedule}) حضور دارد ")
            CA_3 = conflicting_assignments.filter(supervisor3=supervisor)
            if supervisor and CA_3.exists():
                raise ValidationError(
                    f"استاد {supervisor} به عنوان استاد مشاور اول در همین زمان در نشست دیگری ({CA_3.last().title} - {CA_3.last().schedule}) حضور دارد ")
            CA_4 = conflicting_assignments.filter(supervisor4=supervisor)
            if supervisor and CA_4.exists():
                raise ValidationError(
                    f"استاد {supervisor} به عنوان استاد مشاور دوم در همین زمان در نشست دیگری ({CA_4.last().title} - {CA_4.last().schedule}) حضور دارد ")

        # Check for conflict with graduate monitor with other graduate monitor
        CA_5 = conflicting_assignments.filter(graduate_monitor=self.graduate_monitor)
        if self.graduate_monitor and CA_5.exists():
            raise ValidationError(
                f"استاد {self.graduate_monitor} به عنوان ناظر تحصیلات تکمیلی در همین زمان در نشست دیگری ({CA_4.last().title} - {CA_4.last().schedule}) حضور دارد "
            )

        # Ensure that a supervisor cannot also be the graduate monitor
        if self.graduate_monitor in supervisors:
            raise ValidationError("ناظر تکمیلی نمیتواند به عنوان استاد راهنما یا استاد مشاور حضور داشته باشد !")

        # Ensure that no supervisor is assigned more than once
        non_null_supervisors = [s for s in supervisors if s is not None]
        if len(set(non_null_supervisors)) != len(non_null_supervisors):
            raise ValidationError("هر استاد راهنما نمی‌تواند بیش از یک بار به عنوان استاد راهنما یا مشاور انتخاب شود.")