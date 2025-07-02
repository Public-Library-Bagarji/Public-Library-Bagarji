from django.core.management.base import BaseCommand
from library_admin.models import BlogComment, BookComment, BookReviewComment, NewsComment

class Command(BaseCommand):
    help = 'Find comments with bad parent references.'

    def handle(self, *args, **options):
        models = [BlogComment, BookComment, BookReviewComment, NewsComment]
        found = False
        for model in models:
            model_name = model.__name__
            for c in model.objects.exclude(parent=None):
                if not isinstance(c.parent_id, int):
                    self.stdout.write(self.style.ERROR(f"{model_name} id={c.id} has non-integer parent_id: {c.parent_id} (type: {type(c.parent_id)})"))
                    found = True
                elif not c.parent or not hasattr(c.parent, 'id') or not isinstance(c.parent, model):
                    self.stdout.write(self.style.ERROR(f"{model_name} id={c.id} has invalid parent: {repr(c.parent)} (parent_id: {c.parent_id})"))
                    found = True
        if not found:
            self.stdout.write(self.style.SUCCESS("No bad parent references found!")) 