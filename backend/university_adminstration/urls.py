from django.urls import path
from .views import GetEducationalGroupsView

urlpatterns = [
    path('api/educational-groups/', GetEducationalGroupsView.as_view(), name='get_educational_groups'),
]