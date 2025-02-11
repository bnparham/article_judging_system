from django.contrib import admin, messages
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

    def clean(self):
        cleaned_data = super(ScheduleForm, self).clean()
        self.scheduleID = self.instance.id

        self.year = cleaned_data.get('year')
        self.semester = cleaned_data.get('semester')
        self.start_date = date2jalali(cleaned_data.get('start_date'))
        self.end_date = date2jalali(cleaned_data.get('end_date'))

        if self.start_date.year != self.year:
            messages.error(self.request, "سال تاریخ شروع نیم سال تخصیلی با سال انتخاب شده تطابق ندارد")
            raise forms.ValidationError(f'')
        if self.end_date.year != self.year:
            messages.error(self.request, "سال تاریخ پایان نیم سال تحصیلی با سال انتخاب شده تطابق ندارد")
            raise forms.ValidationError(f'')
        if self.start_date > self.end_date:
            messages.error(self.request, "تاریخ پایان نیم سال تحصیلی نمیتواند قبل از تاریخ شروع آن باشد")
            raise forms.ValidationError(f'')

class ScheduleAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    form = ScheduleForm

    list_display = ('year', 'semester', 'get_start_date_jalali', 'get_end_date_jalali')
    list_filter = ('semester',)
    search_fields = ('year',)
    ordering = ('-year',)

    def get_form(self, request, *args, **kwargs):
        form = super(ScheduleAdmin, self).get_form(request, *args, **kwargs)
        form.request = request  # Pass the request object to the form
        return form

    @admin.display(description='تاریخ شروع نیم سال تحصیلی', ordering='updated_at')
    def get_start_date_jalali(self, obj):
        if obj.start_date:
            return date2jalali(obj.start_date).strftime('%a, %d %b %Y')
        else:
            return "ثبت نشده است"

    @admin.display(description='تاریخ پایان نیم سال تحصیلی', ordering='date')
    def get_end_date_jalali(self, obj):
        if obj.end_date:
            return date2jalali(obj.end_date).strftime('%a, %d %b %Y')
        else:
            return "ثبت نشده است"

admin.site.register(Schedule, ScheduleAdmin)
