from django.apps import AppConfig


class RolesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'roles'

    def ready(self):
        "Connects signals when app is ready"
        import roles.signals
