from django.db import models
from jalali_date import datetime2jalali, date2jalali
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, date


def current_year_choices():
    current_year = date2jalali(date.today()).year
    return [(year, year) for year in range(1396, current_year + 1)]

class Schedule(models.Model):

    SEMESTER_CHOICES = {
        'one':
            'نیم سال اول',
        'two':
            'نیم سال دوم',
    }

    year = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1396),  # Earliest year to allow
            # MaxValueValidator(date2jalali(date.today()).year)  # Restrict to the current year or earlier
        ],
        choices=current_year_choices(),  # Use a dynamic list of choices
        blank=False,
        null=False,
        verbose_name="انتخاب سال",
        default=1396,
    )

    semester = models.CharField(max_length=10,
                            verbose_name='نیم سال تحصیلی',
                            choices=SEMESTER_CHOICES,
                            default=SEMESTER_CHOICES['one'],
                            null=False,
                            blank=False)

    def __str__(self):
        return f" سال {self.year} - {self.SEMESTER_CHOICES[self.semester]}"

    class Meta:
        verbose_name = "نیم سال تحصیلی"
        verbose_name_plural = "نیم سال های تحصیلی"
        constraints = [
            models.UniqueConstraint(fields=['year', 'semester'], name='unique_year_semester',)]
