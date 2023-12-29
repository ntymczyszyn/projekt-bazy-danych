from django.apps import AppConfig


class PromedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'promed'

    def ready(self):
        import promed.signals 
