from django.urls import path
from . import views

urlpatterns = [
    path('admin/session/filter_supervisors/<int:schedule_id>/<int:sessionId>/', views.filter_supervisors, name='filter_supervisors_int'),
    path('admin/session/filter_supervisors/<int:schedule_id>/<str:sessionId>/', views.filter_supervisors,
         name='filter_supervisors_str'),
    path('admin/session/filter_graduate_monitor/<int:schedule_id>/<int:sessionId>/', views.filter_graduate_monitor,
         name='filter_graduate_monitor_int'),
    path('admin/session/filter_graduate_monitor/<int:schedule_id>/<str:sessionId>/', views.filter_graduate_monitor,
         name='filter_graduate_monitor_str'),
    path('admin/session/filter_judges/<int:schedule_id>/<int:sessionId>/', views.filter_judge,
         name='filter_judge_int'),
    path('admin/session/filter_judges/<int:schedule_id>/<str:sessionId>/', views.filter_judge,
         name='filter_judge_str'),
]
