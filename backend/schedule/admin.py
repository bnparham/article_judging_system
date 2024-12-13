from django.contrib import admin
from django.utils.timezone import localtime
from jalali_date import datetime2jalali
from jalali_date.admin import ModelAdminJalaliMixin
from jalali_date.widgets import AdminJalaliDateWidget
from django_flatpickr.widgets import TimePickerInput  # Import Flatpickr widget
from django import forms
from .models import Schedule
from django.utils.translation import gettext_lazy as _


class MonthFilter(admin.SimpleListFilter):
    title = _('ماه')
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        return (
            ('1', _('دی')),
            ('2', _('بهمن')),
            ('3', _('اسفند')),
            ('4', _('فروردین')),
            ('5', _('اردیبهشت')),
            ('6', _('خرداد')),
            ('7', _('تیر')),
            ('8', _('مرداد')),
            ('9', _('شهریور')),
            ('10', _('مهر')),
            ('11', _('آبان')),
            ('12', _('آذر')),
        )

    def queryset(self, request, queryset):
        if self.value():
            if(hasattr(queryset.model, 'date')):
                return queryset.filter(date__month=self.value())


class ScheduleAdminForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = '__all__'
        widgets = {
            'date': AdminJalaliDateWidget,  # Jalali date picker
            'time': TimePickerInput,  # Time picker
        }

class ScheduleAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    form = ScheduleAdminForm
    list_display = ('name', 'get_date_jalali', 'get_time_persian', 'is_active', 'get_created_at_jalali')
    list_filter = ('is_active', MonthFilter)
    search_fields = ('name', 'description')
    ordering = ('-created_at',)


    @admin.display(description='تاریخ', ordering='date')
    def get_date_jalali(self, obj):
        if obj.date:
            # Combine date with a default time to convert to datetime
            from datetime import datetime
            date_as_datetime = datetime.combine(obj.date, datetime.min.time())
            return datetime2jalali(date_as_datetime).strftime('%a, %d %b %Y')
        else:
            return "ثبت نشده است"

    @admin.display(description="زمان", ordering="time")
    def get_time_persian(self, obj):
        if obj.time:
            # Convert time to Persian 12-hour format
            time = obj.time
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

    @admin.display(description='ساخته شده در زمان تاریخ', ordering='created_at')
    def get_created_at_jalali(self, obj):
        if obj.created_at:
            return datetime2jalali(obj.created_at).strftime('%a, %d %b %Y | %H:%M:%S')
        else:
            return "ثبت نشده است"

admin.site.register(Schedule, ScheduleAdmin)
