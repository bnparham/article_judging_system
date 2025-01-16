from django.contrib import admin
from django.utils.timezone import localtime
from jalali_date import datetime2jalali
from jalali_date.admin import ModelAdminJalaliMixin
from jalali_date.widgets import AdminJalaliDateWidget
from django_flatpickr.widgets import TimePickerInput  # Import Flatpickr widget
from django import forms
from .models import Schedule
from django.utils.translation import gettext_lazy as _

class ScheduleAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ('year', 'semester')
    list_filter = ('semester',)
    search_fields = ('year',)
    ordering = ('-year',)

admin.site.register(Schedule, ScheduleAdmin)
