from django.contrib import admin
from django.utils.timezone import localtime
from jalali_date import datetime2jalali
from jalali_date.admin import ModelAdminJalaliMixin
from jalali_date.widgets import AdminJalaliDateWidget
from django_flatpickr.widgets import TimePickerInput  # Import Flatpickr widget
from django import forms
from .models import Schedule
from django.utils.translation import gettext_lazy as _
from jalali_date import datetime2jalali, date2jalali
from datetime import datetime, date

class ScheduleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_year = date2jalali(date.today()).year
        self.fields['year'].choices = [(year, year) for year in range(1396, current_year + 1)]

    class Meta:
        model = Schedule
        fields = '__all__'

class ScheduleAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    form = ScheduleForm

    list_display = ('year', 'semester')
    list_filter = ('semester',)
    search_fields = ('year',)
    ordering = ('-year',)

admin.site.register(Schedule, ScheduleAdmin)
