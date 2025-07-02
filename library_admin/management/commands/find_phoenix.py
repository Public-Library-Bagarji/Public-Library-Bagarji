from django.core.management.base import BaseCommand
from django.apps import apps
from django.db.models import CharField, TextField

class Command(BaseCommand):
    help = "Find any occurrence of the string 'Phoenix' in all CharField and TextField fields of all models in library_admin."

    def handle(self, *args, **options):
        found = False
        for model in apps.get_app_config('library_admin').get_models():
            fields = [f for f in model._meta.get_fields() if isinstance(f, (CharField, TextField))]
            for obj in model.objects.all():
                for field in fields:
                    value = getattr(obj, field.name, None)
                    if isinstance(value, str) and 'Phoenix' in value:
                        self.stdout.write(self.style.ERROR(f"{model.__name__} id={obj.id} field={field.name}: {value}"))
                        found = True
        if not found:
            self.stdout.write(self.style.SUCCESS("No occurrence of 'Phoenix' found in any model field.")) 