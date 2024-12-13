from django.db import models
from jalali_date import datetime2jalali


class Schedule(models.Model):
    name = models.CharField(
        max_length=255,
        help_text="نام یا عنوان برنامه",
        verbose_name='نام'
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="توضیحات اختیاری درباره برنامه",
        verbose_name='توضیحات'

    )
    date = models.DateField(
        help_text="تاریخ برنامه",
        verbose_name='تاریخ',
    )
    time = models.TimeField(
        help_text="زمان برنامه",
        verbose_name='زمان'
    )
    is_active = models.BooleanField(
        default=True,
        help_text="آیا این برنامه فعال است؟",
        verbose_name='فعال بودن'

    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="زمان ایجاد برنامه",
        verbose_name='ساخته شده در زمان/تاریخ"'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="زمان آخرین به‌روزرسانی برنامه",
        verbose_name='آخرین ویرایش در زمان/تاریخ'

    )

    def __str__(self):
        return f"{self.name} در {self.get_date_jalali} ساعت {self.get_time_persian}"

    @property
    def get_date_jalali(self):
        if self.date:
            # Combine date with a default time to convert to datetime
            from datetime import datetime
            date_as_datetime = datetime.combine(self.date, datetime.min.time())
            return datetime2jalali(date_as_datetime).strftime('%a, %d %b %Y')
        else:
            return "ثبت نشده است"

    @property
    def get_time_persian(self):
        if self.time:
            # Convert time to Persian 12-hour format
            time = self.time
            hour = time.hour
            minute = time.minute

            # Determine AM/PM and adjust the hour
            if hour == 0:
                period = "بامداد"
                hour = 12
            elif 1 <= hour < 12:
                period = "صبح"
            elif 12 <= hour <= 17:
                period = "ظهر"
                hour -= 12
            else:
                period = "عصر"
                hour -= 12

            return f"{hour} {period} و {minute} دقیقه"
        else:
            return "ثبت نشده است"

    class Meta:
        verbose_name = "برنامه"
        verbose_name_plural = "برنامه‌ها"
