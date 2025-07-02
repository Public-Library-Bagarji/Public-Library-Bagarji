from django.contrib import admin
from .models import BlogComment, BookComment, BookReviewComment, NewsComment

# @admin.register(BlogComment)
# class BlogCommentAdmin(admin.ModelAdmin):
#     list_display = ('article', 'name', 'comment', 'date', 'is_active')
#     search_fields = ('article__title', 'name', 'comment')
#     list_filter = ('date', 'is_active')

# @admin.register(BookComment)
# class BookCommentAdmin(admin.ModelAdmin):
#     list_display = ('book', 'name', 'comment', 'date', 'is_active')
#     search_fields = ('book__title', 'name', 'comment')
#     list_filter = ('date', 'is_active')

# @admin.register(BookReviewComment)
# class BookReviewCommentAdmin(admin.ModelAdmin):
#     list_display = ('review', 'name', 'comment', 'date', 'is_active')
#     search_fields = ('review__book__title', 'name', 'comment')
#     list_filter = ('date', 'is_active')

# @admin.register(NewsComment)
# class NewsCommentAdmin(admin.ModelAdmin):
#     list_display = ('news', 'name', 'comment', 'date', 'is_active')
#     search_fields = ('news__title', 'name', 'comment')
#     list_filter = ('date', 'is_active')
