from django.db import models

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
        return f"{self.name} در {self.date} ساعت {self.time}"

    class Meta:
        verbose_name = "برنامه"
        verbose_name_plural = "برنامه‌ها"
