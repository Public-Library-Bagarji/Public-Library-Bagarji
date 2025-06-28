from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import render, redirect
from .models import Book, Article, News, BookReview, BlogComment, BookReviewComment, NewsComment, BookComment, Category, Keyword
from django.contrib import messages
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User, Group
from public_site.models import UserProfile
from django.contrib.sites.models import Site
from simple_history.admin import SimpleHistoryAdmin

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

class NewsCommentInline(admin.TabularInline):
    model = NewsComment
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

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'publication_date')
    search_fields = ('title', 'author', 'description')
    list_filter = ('category', 'publication_date')
    inlines = [BookCommentInline]

class ArticleAdminForm(forms.ModelForm):
    keywords_input = forms.CharField(
        label="Keywords (comma or newline separated)",
        required=False,
        widget=forms.Textarea(attrs={"rows":2, "placeholder": "e.g. python, django, ai"})
    )

    class Meta:
        model = Article
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Show existing keywords as comma separated
            self.fields['keywords_input'].initial = ', '.join([k.word for k in self.instance.keywords.all()])

    def clean_keywords_input(self):
        data = self.cleaned_data.get('keywords_input', '')
        # Split by comma or newline
        keywords = [k.strip() for k in data.replace('\n', ',').split(',') if k.strip()]
        return keywords

    def save(self, commit=True):
        instance = super().save(commit=False)
        keywords = self.cleaned_data.get('keywords_input', [])
        if commit:
            instance.save()
            # Assign keywords
            keyword_objs = []
            for word in keywords:
                obj, _ = Keyword.objects.get_or_create(word=word)
                keyword_objs.append(obj)
            instance.keywords.set(keyword_objs)
        else:
            # For commit=False, set keywords after instance is saved
            self._pending_keywords = keywords
        return instance

    def save_m2m(self):
        super().save_m2m()
        if hasattr(self, '_pending_keywords'):
            keyword_objs = []
            for word in self._pending_keywords:
                obj, _ = Keyword.objects.get_or_create(word=word)
                keyword_objs.append(obj)
            self.instance.keywords.set(keyword_objs)

class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'author', 'category', 'keywords_input', 'image')
        }),
    )
    list_display = ('title', 'author', 'publication_date', 'category', 'image_tag')
    search_fields = ('title', 'content', 'author', 'category__name', 'keywords__word')
    list_filter = ('category',)
    # autocomplete_fields = ['category', 'keywords']
    filter_horizontal = ('keywords',)
    inlines = [BlogCommentInline]

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 80px;" />', obj.image.url)
        return ""
    image_tag.short_description = 'Image'

class BookReviewAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('book', 'reviewer_name', 'rating', 'review_text', 'image')
        }),
    )
    list_display = ('book', 'reviewer_name', 'rating', 'review_date', 'image_tag')
    search_fields = ('book__title', 'reviewer_name', 'review_text')
    list_filter = ('rating',)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 80px;" />', obj.image.url)
        return ""
    image_tag.short_description = 'Image'

@admin.register(BookReviewComment)
class BookReviewCommentAdmin(admin.ModelAdmin):
    list_display = ('review', 'name', 'rating', 'date')
    list_filter = ('rating', 'date')
    search_fields = ('name', 'comment')
    readonly_fields = ('date',)

@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'name', 'rating', 'date')
    list_filter = ('rating', 'date')
    search_fields = ('name', 'comment')
    readonly_fields = ('date',)

@admin.register(NewsComment)
class NewsCommentAdmin(admin.ModelAdmin):
    list_display = ('news', 'name', 'rating', 'date')
    list_filter = ('rating', 'date')
    search_fields = ('name', 'comment')
    readonly_fields = ('date',)

@admin.register(BookComment)
class BookCommentAdmin(admin.ModelAdmin):
    list_display = ('book', 'name', 'rating', 'date')
    list_filter = ('rating', 'date')
    search_fields = ('name', 'comment')
    readonly_fields = ('date',)

class NewsAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'category', 'image')
        }),
    )
    list_display = ('title', 'publication_date', 'category', 'image_tag')
    search_fields = ('title', 'content', 'category')
    list_filter = ('category',)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 80px;" />', obj.image.url)
        return ""
    image_tag.short_description = 'Image'

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
        # Gather all comments from all models
        blog_comments = BlogComment.objects.all()
        book_comments = BookComment.objects.all()
        bookreview_comments = BookReviewComment.objects.all()
        news_comments = NewsComment.objects.all()
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

# Unregister UserProfile so it doesn't show as 'User Profiles'
try:
    admin.site.unregister(UserProfile)
except admin.sites.NotRegistered:
    pass

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

admin.site.register(Book, SimpleHistoryAdmin)
admin.site.register(Category, SimpleHistoryAdmin)
admin.site.register(Keyword, SimpleHistoryAdmin)
admin.site.register(News, SimpleHistoryAdmin)
admin.site.register(BookReview, SimpleHistoryAdmin)
admin.site.register(Article, SimpleHistoryAdmin)

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
