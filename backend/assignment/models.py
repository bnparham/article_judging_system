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
                    f"کلاس با شناسه {self.id} تداخل زمانی دارد با نشست دیگری ({session.start_time} - {session.end_time}) در {self.get_date_jalali}."
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
                    f"تداخل زمانی رخ داده است. استاد {professor} در کلاس دیگری با شناسه ({session.id}) در تاریخ {self.get_date_jalali} و بازه زمانی {session.start_time} تا {session.end_time} حضور دارد."
                )


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
