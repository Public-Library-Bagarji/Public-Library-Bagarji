from django.core.management.base import BaseCommand
from library_admin.models import BlogComment, BookComment, BookReviewComment, NewsComment

class Command(BaseCommand):
    help = 'Clean up bad parent references in comment models.'

    def handle(self, *args, **options):
        models = [BlogComment, BookComment, BookReviewComment, NewsComment]
        total_fixed = 0
        for model in models:
            model_name = model.__name__
            all_ids = set(model.objects.values_list('id', flat=True))
            # Fix parent_id that is not an integer or not in all_ids
            bad_comments = model.objects.exclude(parent=None).filter(parent_id__isnull=False)
            count = 0
            for c in bad_comments:
                # Defensive: parent_id must be int and exist
                try:
                    pid = int(c.parent_id)
                except Exception:
                    self.stdout.write(self.style.WARNING(f"{model_name} id={c.id}: parent_id is not an int ({c.parent_id}), setting to None"))
                    c.parent = None
                    c.save()
                    count += 1
                    continue
                if pid not in all_ids:
                    self.stdout.write(self.style.WARNING(f"{model_name} id={c.id}: parent_id {pid} does not exist, setting to None"))
                    c.parent = None
                    c.save()
                    count += 1
            if count:
                self.stdout.write(self.style.SUCCESS(f"Fixed {count} bad parent references in {model_name}"))
            total_fixed += count
        if total_fixed == 0:
            self.stdout.write(self.style.SUCCESS("No bad parent references found!"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Total fixed: {total_fixed}")) 