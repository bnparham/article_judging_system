from django.apps import AppConfig
from django.contrib.auth.apps import AuthConfig

class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'
    verbose_name = "داشبورد حساب کاربری"

    def ready(self):
        import account.signals



AuthConfig.verbose_name = "بررسی اصالت ها و اجازه ها"