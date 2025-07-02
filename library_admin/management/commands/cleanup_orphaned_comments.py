from django.core.management.base import BaseCommand
from library_admin.models import CommentReply
from comments.models import BookReviewComment, BlogComment, NewsComment, BookComment

class Command(BaseCommand):
    help = 'Delete orphaned CommentReply objects and orphaned user comments/replies.'

    def handle(self, *args, **options):
        total_deleted = 0
        # BookReviewComment
        deleted = CommentReply.objects.filter(comment_type='bookreview').exclude(comment_id__in=BookReviewComment.objects.values_list('id', flat=True)).delete()[0]
        total_deleted += deleted
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted} orphaned admin replies for BookReviewComment.'))
        # BlogComment
        deleted = CommentReply.objects.filter(comment_type='blog').exclude(comment_id__in=BlogComment.objects.values_list('id', flat=True)).delete()[0]
        total_deleted += deleted
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted} orphaned admin replies for BlogComment.'))
        # NewsComment
        deleted = CommentReply.objects.filter(comment_type='news').exclude(comment_id__in=NewsComment.objects.values_list('id', flat=True)).delete()[0]
        total_deleted += deleted
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted} orphaned admin replies for NewsComment.'))
        # BookComment
        deleted = CommentReply.objects.filter(comment_type='book').exclude(comment_id__in=BookComment.objects.values_list('id', flat=True)).delete()[0]
        total_deleted += deleted
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted} orphaned admin replies for BookComment.'))
        self.stdout.write(self.style.SUCCESS(f'Total orphaned admin replies deleted: {total_deleted}'))

        # (Optional) Delete orphaned user comments/replies if needed
        # Example for BookReviewComment replies:
        # BookReviewComment.objects.filter(parent_id__isnull=False).exclude(parent_id__in=BookReviewComment.objects.values_list('id', flat=True)).delete()
        # Similar logic can be applied for other comment models if required. 