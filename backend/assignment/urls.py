from django.urls import path
from . import views

urlpatterns = [
    path('admin/session/filter_supervisors/<int:schedule_id>/<int:sessionId>/', views.filter_supervisors, name='filter_supervisors'),
    path('admin/session/filter_supervisors/<int:schedule_id>/<str:sessionId>/', views.filter_supervisors,
         name='filter_supervisors'),
]
