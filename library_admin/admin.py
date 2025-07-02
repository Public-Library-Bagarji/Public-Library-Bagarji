from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Article, News, BookReview, Category
from django.contrib import messages
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User, Group
from public_site.models import UserProfile
from django.contrib.sites.models import Site
from simple_history.admin import SimpleHistoryAdmin
from django.utils.safestring import mark_safe
from django.db.models import Model
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.utils.translation import gettext_lazy as _
from comments.models import BookReviewComment, BlogComment, NewsComment, BookComment
from django.utils.text import Truncator
from library_admin.models import CommentReply

# Register your models here.
class BookReviewCommentInline(admin.TabularInline):
    model = BookReviewComment
    extra = 0
    fields = ('name', 'comment', 'rating', 'date')
    readonly_fields = ('date',)
    can_delete = False

class BookReviewInline(admin.TabularInline):
    model = BookReview
    extra = 0
    fields = ('reviewer_name', 'rating', 'review_text', 'review_date')
    readonly_fields = ('review_date',)
    can_delete = False

class BlogCommentInline(admin.TabularInline):
    model = BlogComment
    extra = 0
    fields = ('name', 'comment', 'rating', 'date')
    readonly_fields = ('date',)
    can_delete = False

class BookCommentInline(admin.TabularInline):
    model = BookComment
    extra = 0
    fields = ('name', 'comment', 'rating', 'date')
    readonly_fields = ('date',)
    can_delete = False

class BookCategoryWidget(ForeignKeyRawIdWidget):
    def url_parameters(self):
        params = super().url_parameters()
        params['type'] = 'book'
        return params

class BlogCategoryWidget(ForeignKeyRawIdWidget):
    def url_parameters(self):
        params = super().url_parameters()
        params['type'] = 'blog'
        return params

class NewsCategoryWidget(ForeignKeyRawIdWidget):
    def url_parameters(self):
        params = super().url_parameters()
        params['type'] = 'news'
        return params

class BookAdminForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use only active book categories
        self.fields['category'].queryset = Category.objects.filter(type='book', active=True)
        self.fields['category'].empty_label = None

class BookAdmin(admin.ModelAdmin):
    form = BookAdminForm
    list_display = ('title', 'author', 'category', 'publication_date')
    search_fields = ('title', 'author', 'description')
    list_filter = ('category', 'publication_date')
    inlines = [BookCommentInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            kwargs['queryset'] = Category.objects.filter(type='book', active=True)
            # Set default type for add popup
            request._category_type_default = 'book'
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class ArticleAdminForm(forms.ModelForm):
    # Remove all keywords_input, keywords, and related logic from forms and admin classes

    class Meta:
        model = Article
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use only active blog categories
        self.fields['category'].queryset = Category.objects.filter(type='blog', active=True)
        self.fields['category'].empty_label = None

class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'author', 'category', 'image')
        }),
    )
    list_display = ('title', 'author', 'publication_date', 'category', 'image_tag')
    search_fields = ('title', 'content', 'author', 'category__name')
    list_filter = ('category',)
    inlines = [BlogCommentInline]

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 80px;" />', obj.image.url)
        return ""
    image_tag.short_description = 'Image'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            kwargs['queryset'] = Category.objects.filter(type='blog', active=True)
            request._category_type_default = 'blog'
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class BookReviewAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('book', 'reviewer_name', 'review_text', 'image')
        }),
    )
    list_display = ('book', 'reviewer_name', 'review_date', 'image_tag')
    search_fields = ('book__title', 'reviewer_name', 'review_text')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 80px;" />', obj.image.url)
        return ""
    image_tag.short_description = 'Image'

# Helper function to truncate text
def truncate_text(text, length):
    return Truncator(text).chars(length, truncate='...')

class BaseCommentAdmin(SimpleHistoryAdmin):
    """
    A base admin class for comment models to provide a consistent,
    hierarchical display for comments and their replies.
    """
    list_display = ('indented_comment', 'user_link', 'reply_count', 'date')
    list_filter = ('date',)
    search_fields = ('user__username', 'comment')
    readonly_fields = ('date',)

    def indented_comment(self, obj):
        """
        Displays the comment content. If it's a reply, it's indented
        and prefixed with 'Re: '.
        """
        if obj.parent:
            return mark_safe(f"&nbsp;&nbsp;&nbsp;↳&nbsp;Re: {truncate_text(obj.comment, 25)}")
        return truncate_text(obj.comment, 25)
    indented_comment.short_description = 'Comment'

    def user_link(self, obj):
        """Creates a link to the user's admin change page."""
        if obj.user:
            url = reverse('admin:public_site_userprofile_change', args=[obj.user.userprofile.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "Anonymous"
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(parent__isnull=True).order_by('-date')

    def reply_count(self, obj):
        def count_replies(comment):
            total = comment.replies.count()
            for reply in comment.replies.all():
                total += count_replies(reply)
            return total
        count = count_replies(obj)
        if count == 0:
            return 'No Reply'
        # Make the count a clickable link to the replies view
        url = f"replies/{obj.pk}/"
        return format_html('<a href="{}">{}</a>', url, f'{count} Reply' if count == 1 else f'{count} Replies')
    reply_count.short_description = 'Replies'
    reply_count.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('replies/<int:comment_id>/', self.admin_site.admin_view(self.view_replies), name=f'{self.model._meta.app_label}_{self.model._meta.model_name}_replies'),
        ]
        return custom_urls + urls

    def view_replies(self, request, comment_id):
        comment = get_object_or_404(self.model, pk=comment_id)
        # Gather all replies recursively
        def get_all_replies(comment):
            replies = list(comment.replies.all())
            all_replies = []
            for reply in replies:
                all_replies.append(reply)
                all_replies.extend(get_all_replies(reply))
            return all_replies
        all_replies = get_all_replies(comment)
        # Map model_name to correct comment_type
        model_name_map = {
            'bookreviewcomment': 'bookreview',
            'blogcomment': 'blog',
            'newscomment': 'news',
            'bookcomment': 'book',
        }
        comment_type = model_name_map.get(self.model._meta.model_name, self.model._meta.model_name)
        admin_replies = CommentReply.objects.filter(comment_id=comment.id, comment_type=comment_type, is_active=True).order_by('date')

        # Handle admin reply creation
        message = None
        if request.method == 'POST':
            if 'admin_reply' in request.POST:
                reply_text = request.POST.get('admin_reply', '').strip()
                if reply_text:
                    CommentReply.objects.create(
                        comment_type=comment_type,
                        comment_id=comment.id,
                        reply=reply_text,
                        admin_name=request.user.username
                    )
                    message = 'Admin reply added.'
                    return redirect(request.path)
            elif 'delete_admin_reply' in request.POST:
                reply_id = request.POST.get('delete_admin_reply')
                CommentReply.objects.filter(id=reply_id, comment_id=comment.id).delete()
                message = 'Admin reply deleted.'
                return redirect(request.path)
            elif 'delete_public_reply' in request.POST:
                reply_id = request.POST.get('delete_public_reply')
                # Delete the public reply (and its children recursively)
                self.model.objects.filter(id=reply_id).delete()
                message = 'User reply deleted.'
                return redirect(request.path)

        context = dict(
            self.admin_site.each_context(request),
            comment=comment,
            replies=all_replies,
            admin_replies=admin_replies,
            message=message,
        )
        return render(request, "admin/comment_replies.html", context)

@admin.register(BookReviewComment)
class BookReviewCommentAdmin(BaseCommentAdmin):
    def book_name(self, obj):
        return truncate_text(obj.review.book.title, 20)
    book_name.short_description = 'Book'

    list_display = ('book_name', 'indented_comment', 'user_link', 'reply_count', 'date')
    list_filter = ('date',)

@admin.register(BlogComment)
class BlogCommentAdmin(BaseCommentAdmin):
    def article_name(self, obj):
        return truncate_text(obj.article.title, 20)
    article_name.short_description = 'Article'

    list_display = ('article_name', 'indented_comment', 'user_link', 'reply_count', 'date')
    list_filter = ('date',)

@admin.register(NewsComment)
class NewsCommentAdmin(BaseCommentAdmin):
    def news_title(self, obj):
        return truncate_text(obj.news.title, 20)
    news_title.short_description = 'News'

    list_display = ('news_title', 'indented_comment', 'user_link', 'reply_count', 'date')
    list_filter = ('date',)

@admin.register(BookComment)
class BookCommentAdmin(BaseCommentAdmin):
    def book_name(self, obj):
        return truncate_text(obj.book.title, 20)
    book_name.short_description = 'Book'

    list_display = ('book_name', 'indented_comment', 'user_link', 'reply_count', 'date')
    list_filter = ('date',)

class NewsAdminForm(forms.ModelForm):
    class Meta:
        model = News
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use only active news categories
        self.fields['category'].queryset = Category.objects.filter(type='news', active=True)
        self.fields['category'].empty_label = None

class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'category', 'image')
        }),
    )
    list_display = ('title', 'publication_date', 'category', 'image_tag')
    search_fields = ('title', 'content', 'category__name')
    list_filter = ('category',)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 80px;" />', obj.image.url)
        return ""
    image_tag.short_description = 'Image'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            kwargs['queryset'] = Category.objects.filter(type='news', active=True)
            request._category_type_default = 'news'
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Unregister individual comment models so they don't appear in the sidebar
# admin.site.unregister(BlogComment)
# admin.site.unregister(BookComment)
# admin.site.unregister(BookReviewComment)
# admin.site.unregister(NewsComment)

class CommentsAdmin(admin.ModelAdmin):
    change_list_template = "admin/comments_changelist.html"
    model = None  # Not tied to a single model

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('comments/', self.admin_site.admin_view(self.comments_view), name='comments_dashboard'),
        ]
        return custom_urls + urls

    def comments_view(self, request):
        # Gather only top-level (parent) comments from all models
        # Note: The filtering is now handled in BaseCommentAdmin.get_queryset,
        # but we do it here explicitly for the combined view to be safe.
        blog_comments = BlogComment.objects.filter(parent__isnull=True)
        book_comments = BookComment.objects.filter(parent__isnull=True)
        bookreview_comments = BookReviewComment.objects.filter(parent__isnull=True)
        news_comments = NewsComment.objects.filter(parent__isnull=True)
        
        # Combine and sort by date (latest first)
        all_comments = list(blog_comments) + list(book_comments) + list(bookreview_comments) + list(news_comments)
        all_comments.sort(key=lambda c: c.date, reverse=True)

        # Handle delete
        if request.method == 'POST' and 'delete_comment_id' in request.POST:
            comment_id = int(request.POST['delete_comment_id'])
            comment_type = request.POST['delete_comment_type']
            model_map = {
                'blog': BlogComment,
                'book': BookComment,
                'bookreview': BookReviewComment,
                'news': NewsComment,
            }
            model = model_map.get(comment_type)
            if model:
                try:
                    model.objects.get(id=comment_id).delete()
                    messages.success(request, 'Comment deleted successfully!')
                    return redirect(request.path)
                except Exception:
                    messages.error(request, 'Failed to delete comment.')

        context = dict(
            self.admin_site.each_context(request),
            comments=all_comments,
        )
        return render(request, "admin/comments_changelist.html", context)

# Custom User admin for public users (already set in public_site/admin.py)
# Now, register a separate admin for staff/admin users with a custom label
class AdminUserAdmin(DefaultUserAdmin):
    def get_queryset(self, request):
        # Only show staff/admin users
        qs = super().get_queryset(request)
        return qs.filter(is_staff=True)
    class Meta:
        verbose_name = 'Admin User'
        verbose_name_plural = 'Admin Users'

admin.site.register(Book, BookAdmin)
admin.site.register(Category, SimpleHistoryAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(BookReview, SimpleHistoryAdmin)
admin.site.register(Article, ArticleAdmin)

def safe_unregister(model):
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass

# Only unregister Site if still installed
safe_unregister(Site)

# Unregister the Group model from the admin site so the 'Authentication and Authorization' box is removed if no other models are registered under it
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

# Patch CategoryAdmin to set type automatically in popup
from django.contrib import admin as django_admin
from django import forms as django_forms

class CategoryAdminForm(django_forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.request if hasattr(self, 'request') else None
        if request and request.GET.get('_popup') and request.GET.get('type'):
            self.fields['type'].initial = request.GET['type']
            self.fields['type'].widget = django_forms.HiddenInput()

class PatchedCategoryAdmin(SimpleHistoryAdmin):
    form = CategoryAdminForm
    list_filter = ['type', 'active']
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form

admin.site.unregister(Category)
admin.site.register(Category, PatchedCategoryAdmin)
