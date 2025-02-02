from django.http import JsonResponse
from django.views import View
from .models import FacultyEducationalGroup

class GetEducationalGroupsView(View):
    def get(self, request, *args, **kwargs):
        faculty = request.GET.get('faculty')
        if not faculty:
            return JsonResponse({'error': 'Faculty is required'}, status=400)

        # Fetch educational group choices
        educational_groups = FacultyEducationalGroup.EDUCATIONAL_GROUP_CHOICES.get(faculty, [])

        # Return as JSON response
        return JsonResponse({'educational_groups': educational_groups})
