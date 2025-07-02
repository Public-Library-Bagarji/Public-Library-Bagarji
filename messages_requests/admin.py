from django.contrib import admin
from .models import BookRequest, ContactMessage

@admin.register(BookRequest)
class BookRequestAdmin(admin.ModelAdmin):
    list_display = ('book_name', 'author_name', 'user', 'date_created')
    search_fields = ('book_name', 'author_name', 'user__username')
    list_filter = ('date_created',)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_filter = ('created_at',)
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
