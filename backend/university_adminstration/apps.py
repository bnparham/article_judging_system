from django.apps import AppConfig


class UniversityAdminstrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'university_adminstration'
    verbose_name = "داشبورد امور دانشکده"

    def ready(self):
        import university_adminstration.signals