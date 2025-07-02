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
            bad_comments = model.objects.exclude(parent=None).filter(parent_id__isnull=False).exclude(parent_id__in=all_ids)
            count = bad_comments.count()
            for c in bad_comments:
                self.stdout.write(f"Fixing {model_name} id={c.id}: parent_id was {c.parent_id}")
                c.parent = None
                c.save()
            total_fixed += count
            self.stdout.write(f"{model_name}: Fixed {count} bad parent references.")
        self.stdout.write(self.style.SUCCESS(f"Total fixed: {total_fixed}")) 