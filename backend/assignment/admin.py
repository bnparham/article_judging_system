from django.contrib import admin
from .models import Session

class SessionAdmin(admin.ModelAdmin):
    # Fields to be displayed in the list view
    list_display = ('title', 'student', 'schedule', 'supervisor1', 'supervisor2', 'supervisor3', 'supervisor4', 'graduate_monitor', 'session_status', 'created_at', 'updated_at')

    # Fields to be used for searching in the admin interface
    search_fields = ('title', 'student__first_name', 'student__last_name', 'supervisor1__first_name', 'supervisor1__last_name', 'supervisor2__first_name', 'supervisor2__last_name', 'supervisor3__first_name', 'supervisor3__last_name', 'supervisor4__first_name', 'supervisor4__last_name')

    # Filters to narrow down results in the list view
    list_filter = ('session_status', 'schedule')

    # Fields to be shown on the detail/edit page
    fields = ('title', 'description', 'schedule', 'student', 'supervisor1', 'supervisor2', 'supervisor3', 'supervisor4', 'graduate_monitor', 'session_status')

    # Make sure the fields are read-only in certain cases, or configure which ones can be modified
    readonly_fields = ('created_at', 'updated_at')

    # Prepopulate fields if needed (for example, auto-filling some fields)
    # prepopulated_fields = {'description': ('title',)}

    # Custom form validation for saving the object
    def save_model(self, request, obj, form, change):
        # You can perform any custom save logic here
        super().save_model(request, obj, form, change)

# Register the Session model with the custom admin class
admin.site.register(Session, SessionAdmin)
