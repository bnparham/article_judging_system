from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
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
        verbose_name = 'جلسه دفاع پایان نامه / رساله'
        verbose_name_plural = 'جلسات دفاع پایان نامه / رساله'
        constraints = [
            models.UniqueConstraint(fields=['schedule', 'date', 'class_number', 'start_time', 'end_time'],
                                    name='unique_session',)]

    def save(self, *args, **kwargs):
        # Automatically set is_active based on presence of any judge
        self.is_active = any([self.judge1, self.judge2, self.judge3])
        super().save(*args, **kwargs)

    def clean(self):

        if self.start_time >= self.end_time:
            raise ValidationError("تاریخ شروع باید قبل از تاریخ پایان باشد !")

        # Check for time conflicts in the same term (date) and schedule and class_number
        overlapping_sessions = Session.objects.filter(
            date=self.date,  # Same term/date
            schedule=self.schedule,  # Same semester
            class_number=self.class_number,  #Same class
        ).exclude(id=self.id)  # Exclude the current session if it's an update

        # Check if the start and end times of the current session overlap with any existing session
        for session in overlapping_sessions:
            # Time overlap condition:
            # 1. The current session starts during another session.
            # 2. The current session ends during another session.
            # 3. The current session completely spans another session.
            if (
                    (self.start_time >= session.start_time and self.start_time < session.end_time) or
                    (self.end_time > session.start_time and self.end_time <= session.end_time) or
                    (self.start_time <= session.start_time and self.end_time >= session.end_time)
            ):
                raise ValidationError(
                    f"کلاس {self.class_number} تداخل زمانی دارد با نشست دیگری ({session.start_time} - {session.end_time}) در {self.get_date_jalali}."
                )


        # Collect all the roles that should not be duplicated
        roles = [
            self.supervisor1, self.supervisor2, self.supervisor3, self.supervisor4,
            self.judge1, self.judge2, self.judge3,
            self.graduate_monitor
        ]

        # Remove any None values (empty fields)
        roles = [role for role in roles if role is not None]

        # Check for duplicates
        if len(roles) != len(set(roles)):
            raise ValidationError(
                "اساتید تکراری نمی‌توانند در یک نشست تکراری باشند."
            )

        # Remove None values (empty fields)
        professors = [prof for prof in roles if prof is not None]
        overlapping_sessions_2 = Session.objects.filter(
            date=self.date,  # Same term/date
            schedule=self.schedule,  # Same semester
        ).exclude(id=self.id)  # Exclude the current session if it's an update

        # Loop through all professors and check for conflicts
        for professor in professors:

            # Fetch the conflicting sessions
            conflicting_sessions = overlapping_sessions_2.filter(
                (
                    Q(supervisor1=professor) | Q(supervisor2=professor) |
                    Q(supervisor3=professor) | Q(supervisor4=professor) |
                    Q(judge1=professor) | Q(judge2=professor) |
                    Q(judge3=professor) | Q(graduate_monitor=professor)
                )
                &
                (
                    # Q(start_time__lt=self.end_time, start_time__gte=self.start_time) |
                    # Q(end_time__lt=self.end_time, end_time__gt=self.start_time)  # Overlapping time
                    Q(start_time__lt=self.end_time, end_time__gt=self.start_time)  # Time overlaps
                )
            )

            # Check if conflicts exist
            if conflicting_sessions.exists():
                # Fetch the first conflicting session for details
                session = conflicting_sessions.first()
                raise ValidationError(
                    f"تداخل زمانی رخ داده است. استاد {professor} در کلاس دیگری ({session.class_number}) در تاریخ {self.get_date_jalali} و بازه زمانی {session.start_time} تا {session.end_time} حضور دارد."
                )


    @property
    def get_date_jalali(self):
        if self.date:
            return date2jalali(self.date).strftime('%a, %d %b %Y')
        else:
            return "ثبت نشده است"

    # def clean(self):
    #
    #     if not self.schedule_id:
    #         raise ValidationError(f"هیچ زمانبندی برای این نشست انتخاب نشده است !")
    #     if not self.start_time:
    #         raise ValidationError(f"زمان شروع برای این نشست انتخاب نشده است!")
    #     if not self.end_time:
    #         raise ValidationError('هیچ زمان پایانی برای این نشست انتخاب نشده است!')
    #     if not self.class_number:
    #         raise ValidationError('هیچ شماره کلاسی برای این نشست انتخاب نشده است!')
    #     if not self.student:
    #         raise ValidationError(f"هیچ دانشجویی برای این نشست انتخاب نشده است !")
    #     if not self.supervisor1_id:
    #         raise ValidationError(f"هیچ استاد راهنما اولی برای این نشست انتخاب نشده است !")
    #     if not self.graduate_monitor_id:
    #         raise ValidationError(f"هیچ ناظر تحصیلات تکمیلی برای این نشست انتخاب نشده است !")
    #
    #     # Check if the session is being updated
    #     is_updating = self.pk is not None
    #
    #     # Check half-open interval validity
    #     if self.start_time >= self.end_time:
    #         raise ValidationError("تاریخ شروع باید قبل از تاریخ پایان باشد !")
    #
    #     # Query conflicting sessions based on the same schedule, date, class_number
    #     conflicting_sessions = Session.objects.filter(schedule=self.schedule,
    #                                                   date=self.date,
    #                                                   )
    #     if is_updating:
    #         conflicting_sessions = conflicting_sessions.exclude(id=self.id)
    #
    #     # Check for overlapping intervals
    #     overlapping_programs = conflicting_sessions.filter(
    #         Q(start_time__lt=self.end_time) & Q(end_time__gt=self.start_time)
    #     )
    #
    #     if overlapping_programs.exists():
    #         raise ValidationError("تداخل بازه زمان بندی ! جلسه ای در این تاریخ و نیم سال تحصیلی ، در کلاس یکسان وجود دارد")
    #
    #
    #     # Check for conflicts with the student
    #     if conflicting_sessions.filter(student=self.student).exists():
    #         raise ValidationError(f"دانشجو {self.student} در همین زمان در نشست دیگری حضور دارد.")
    #
    #     # Check for conflicts with supervisors and graduate monitor
    #     supervisors = [self.supervisor1, self.supervisor2, self.supervisor3, self.supervisor4]
    #     # Check for conflicts judges  with supervisors and graduate monitor
    #     judges = [self.judge1, self.judge2, self.judge3]
    #
    #     for judge in judges:
    #         if judge:
    #             # Conflict with supervisor roles in other sessions
    #             conflict_roles = conflicting_sessions.filter(
    #                 models.Q(supervisor1=judge) |
    #                 models.Q(supervisor2=judge) |
    #                 models.Q(supervisor3=judge) |
    #                 models.Q(supervisor4=judge)
    #             )
    #             if conflict_roles.exists():
    #                 raise ValidationError(
    #                     f"خطا در انتخاب داور ! "
    #                     f"استاد {judge} در همین زمان به عنوان استاد راهنما یا مشاور در نشست دیگری "
    #                     f"({conflict_roles.last().title} - {conflict_roles.last().schedule}) حضور دارد."
    #                 )
    #
    #             # Conflict with judge roles in other sessions
    #             conflict_roles_2 = conflicting_sessions.filter(
    #                 models.Q(judge1=judge) |
    #                 models.Q(judge2=judge) |
    #                 models.Q(judge3=judge)
    #             )
    #             if conflict_roles_2.exists():
    #                 raise ValidationError(
    #                     f"خطا در انتخاب داور ! "
    #                     f"استاد {judge} در همین زمان به عنوان داور در نشست دیگری "
    #                     f"حضور دارد ({conflict_roles_2.last().title} - {conflict_roles_2.last().schedule})"
    #                 )
    #
    #             # Conflict with graduate monitor
    #             if conflicting_sessions.filter(graduate_monitor=judge).exists():
    #                 raise ValidationError(
    #                     f"خطا در انتخاب داور ! "
    #                     f"استاد {judge} به عنوان ناظر تحصیلات تکمیلی در همین زمان در نشست دیگری حضور دارد."
    #                 )
    #
    #     for supervisor in supervisors:
    #         if supervisor:
    #             # Conflict with supervisor roles in other sessions
    #             conflict_roles = conflicting_sessions.filter(
    #                 models.Q(supervisor1=supervisor) |
    #                 models.Q(supervisor2=supervisor) |
    #                 models.Q(supervisor3=supervisor) |
    #                 models.Q(supervisor4=supervisor)
    #             )
    #             if conflict_roles.exists():
    #                 raise ValidationError(
    #                     f"خطا در انتخاب استاد راهنما یا استاد مشاور ! "
    #                     f"استاد {supervisor} در همین زمان به عنوان استاد راهنما یا مشاور در نشست دیگری "
    #                     f"({conflict_roles.last().title} - {conflict_roles.last().schedule}) حضور دارد."
    #                 )
    #
    #             # Conflict with judge roles in other sessions
    #             conflict_roles_2 = conflicting_sessions.filter(
    #                 models.Q(judge1=supervisor) |
    #                 models.Q(judge2=supervisor) |
    #                 models.Q(judge3=supervisor)
    #             )
    #             if conflict_roles_2.exists():
    #                 raise ValidationError(
    #                     f"خطا در انتخاب استاد راهنما یا استاد مشاور ! "
    #                     f"استاد {supervisor} در همین زمان به عنوان داور در نشست دیگری "
    #                     f"حضور دارد ({conflict_roles_2.last().title} - {conflict_roles_2.last().schedule})"
    #                 )
    #
    #             # Conflict with graduate monitor
    #             if conflicting_sessions.filter(graduate_monitor=supervisor).exists():
    #                 raise ValidationError(
    #                     f"خطا در انتخاب استاد راهنما یا استاد مشاور ! "
    #                     f"استاد {supervisor} به عنوان ناظر تحصیلات تکمیلی در همین زمان در نشست دیگری حضور دارد."
    #                 )
    #
    #     # Conflict with graduate monitor
    #     if conflicting_sessions.filter(graduate_monitor=self.graduate_monitor).exists():
    #         raise ValidationError(
    #             f"خطا در انتخاب ناظر تحصیلات تکمیلی ! "
    #             f"استاد {self.graduate_monitor} به عنوان ناظر تحصیلات تکمیلی در همین زمان در نشست دیگری حضور دارد."
    #         )
    #
    #     # Ensure graduate monitor is not also a supervisor
    #     if self.graduate_monitor in supervisors:
    #         raise ValidationError(
    #             f"خطا در انتخاب ناظر تحصیلات تکمیلی ! "
    #             f"ناظر تحصیلات تکمیلی نمی‌تواند به عنوان استاد راهنما یا مشاور انتخاب شود."
    #              )
    #
    #     # Ensure no supervisor is assigned multiple roles in the same session
    #     non_null_supervisors = [supervisor for supervisor in supervisors if supervisor is not None]
    #     if len(set(non_null_supervisors)) != len(non_null_supervisors):
    #         raise ValidationError(
    #             f"خطا در انتخاب استاد راهنما یا استاد مشاور ! "
    #             f"هر استاد نمی‌تواند بیش از یک بار به عنوان استاد راهنما یا مشاور انتخاب شود."
    #         )
    #
    #     # Ensure no judge is assigned multiple roles in the same session
    #     non_null_judges = [judge for judge in judges if judge is not None]
    #     if len(set(non_null_judges)) != len(non_null_judges):
    #         raise ValidationError(
    #             f"خطا در انتخاب داور ! "
    #             f"هر استاد نمی‌تواند بیش از یک بار به عنوان داور انتخاب شود."
    #         )

    def __str__(self):
        return f"{self.student.name} | {self.schedule} جلسه دفاعیه : "
