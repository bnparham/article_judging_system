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

    judge1 = models.ForeignKey(
        'account.Teacher',
        on_delete=models.CASCADE,
        related_name="judge1_assignments",
        verbose_name="داور اول",
        blank=True,
        null=True,
        help_text="داور اول را انتخاب کنید (انتخاب اختیاری)"
    )
    judge2 = models.ForeignKey(
        'account.Teacher',
        on_delete=models.CASCADE,
        related_name="judge3_assignments",
        verbose_name="داور دوم",
        blank=True,
        null=True,
        help_text="داور دوم را انتخاب کنید (انتخاب اختیاری)"
    )
    judge3 = models.ForeignKey(
        'account.Teacher',
        on_delete=models.CASCADE,
        related_name="judge2_assignments",
        verbose_name="داور سوم",
        blank=True,
        null=True,
        help_text="داور سوم را انتخاب کنید (انتخاب اختیاری)"
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

    def save(self, *args, **kwargs):
        # Automatically set is_active based on presence of any judge
        self.is_active = any([self.judge1, self.judge2, self.judge3])
        super().save(*args, **kwargs)

    def clean(self):

        if not self.schedule_id:
            raise ValidationError(f"هیچ زمانبندی برای این نشست انتخاب نشده است !")
        if not self.title:
            raise ValidationError(f"هیچ عنوانی برای این نشست انتخاب نشده است !")
        if not self.student:
            raise ValidationError(f"هیچ دانشجویی برای این نشست انتخاب نشده است !")
        if not self.supervisor1_id:
            raise ValidationError(f"هیچ استاد راهنما اولی برای این نشست انتخاب نشده است !")
        if not self.graduate_monitor_id:
            raise ValidationError(f"هیچ ناظر تحصیلات تکمیلی برای این نشست انتخاب نشده است !")

        # Check if the session is being updated
        is_updating = self.pk is not None

        # Query conflicting sessions based on the same schedule
        conflicting_sessions = Session.objects.filter(schedule=self.schedule)
        if is_updating:
            conflicting_sessions = conflicting_sessions.exclude(id=self.id)

        # Check for conflicts with the student
        if conflicting_sessions.filter(student=self.student).exists():
            raise ValidationError(f"دانشجو {self.student} در همین زمان در نشست دیگری حضور دارد.")

        # Check for conflicts with supervisors and graduate monitor
        supervisors = [self.supervisor1, self.supervisor2, self.supervisor3, self.supervisor4]
        # Check for conflicts judges  with supervisors and graduate monitor
        judges = [self.judge1, self.judge2, self.judge3]

        for judge in judges:
            if judge:
                # Conflict with supervisor roles in other sessions
                conflict_roles = conflicting_sessions.filter(
                    models.Q(supervisor1=judge) |
                    models.Q(supervisor2=judge) |
                    models.Q(supervisor3=judge) |
                    models.Q(supervisor4=judge)
                )
                if conflict_roles.exists():
                    raise ValidationError(
                        f"خطا در انتخاب داور ! "
                        f"استاد {judge} در همین زمان به عنوان استاد راهنما یا مشاور در نشست دیگری "
                        f"({conflict_roles.last().title} - {conflict_roles.last().schedule}) حضور دارد."
                    )

                # Conflict with judge roles in other sessions
                conflict_roles_2 = conflicting_sessions.filter(
                    models.Q(judge1=judge) |
                    models.Q(judge2=judge) |
                    models.Q(judge3=judge)
                )
                if conflict_roles_2.exists():
                    raise ValidationError(
                        f"خطا در انتخاب داور ! "
                        f"استاد {judge} در همین زمان به عنوان داور در نشست دیگری "
                        f"حضور دارد ({conflict_roles_2.last().title} - {conflict_roles_2.last().schedule})"
                    )

                # Conflict with graduate monitor
                if conflicting_sessions.filter(graduate_monitor=judge).exists():
                    raise ValidationError(
                        f"خطا در انتخاب داور ! "
                        f"استاد {judge} به عنوان ناظر تحصیلات تکمیلی در همین زمان در نشست دیگری حضور دارد."
                    )

        for supervisor in supervisors:
            if supervisor:
                # Conflict with supervisor roles in other sessions
                conflict_roles = conflicting_sessions.filter(
                    models.Q(supervisor1=supervisor) |
                    models.Q(supervisor2=supervisor) |
                    models.Q(supervisor3=supervisor) |
                    models.Q(supervisor4=supervisor)
                )
                if conflict_roles.exists():
                    raise ValidationError(
                        f"خطا در انتخاب استاد راهنما یا استاد مشاور ! "
                        f"استاد {supervisor} در همین زمان به عنوان استاد راهنما یا مشاور در نشست دیگری "
                        f"({conflict_roles.last().title} - {conflict_roles.last().schedule}) حضور دارد."
                    )

                # Conflict with judge roles in other sessions
                conflict_roles_2 = conflicting_sessions.filter(
                    models.Q(judge1=supervisor) |
                    models.Q(judge2=supervisor) |
                    models.Q(judge3=supervisor)
                )
                if conflict_roles_2.exists():
                    raise ValidationError(
                        f"خطا در انتخاب استاد راهنما یا استاد مشاور ! "
                        f"استاد {supervisor} در همین زمان به عنوان داور در نشست دیگری "
                        f"حضور دارد ({conflict_roles_2.last().title} - {conflict_roles_2.last().schedule})"
                    )

                # Conflict with graduate monitor
                if conflicting_sessions.filter(graduate_monitor=supervisor).exists():
                    raise ValidationError(
                        f"خطا در انتخاب استاد راهنما یا استاد مشاور ! "
                        f"استاد {supervisor} به عنوان ناظر تحصیلات تکمیلی در همین زمان در نشست دیگری حضور دارد."
                    )

        # Conflict with graduate monitor
        if conflicting_sessions.filter(graduate_monitor=self.graduate_monitor).exists():
            raise ValidationError(
                f"خطا در انتخاب ناظر تحصیلات تکمیلی ! "
                f"استاد {self.graduate_monitor} به عنوان ناظر تحصیلات تکمیلی در همین زمان در نشست دیگری حضور دارد."
            )

        # Ensure graduate monitor is not also a supervisor
        if self.graduate_monitor in supervisors:
            raise ValidationError(
                f"خطا در انتخاب ناظر تحصیلات تکمیلی ! "
                f"ناظر تحصیلات تکمیلی نمی‌تواند به عنوان استاد راهنما یا مشاور انتخاب شود."
                 )

        # Ensure no supervisor is assigned multiple roles in the same session
        non_null_supervisors = [supervisor for supervisor in supervisors if supervisor is not None]
        if len(set(non_null_supervisors)) != len(non_null_supervisors):
            raise ValidationError(
                f"خطا در انتخاب استاد راهنما یا استاد مشاور ! "
                f"هر استاد نمی‌تواند بیش از یک بار به عنوان استاد راهنما یا مشاور انتخاب شود."
            )

        # Ensure no judge is assigned multiple roles in the same session
        non_null_judges = [judge for judge in judges if judge is not None]
        if len(set(non_null_judges)) != len(non_null_judges):
            raise ValidationError(
                f"خطا در انتخاب داور ! "
                f"هر استاد نمی‌تواند بیش از یک بار به عنوان داور انتخاب شود."
            )

    def __str__(self):
        return f"{self.title} | {self.schedule}"
