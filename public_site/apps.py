from django.apps import AppConfig


class PublicSiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'public_site'
    verbose_name = 'User Management'  # Custom admin box title
