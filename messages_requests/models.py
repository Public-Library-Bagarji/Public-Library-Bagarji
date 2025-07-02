from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class BookRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book_name = models.CharField(max_length=200)
    author_name = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.book_name} by {self.author_name} (requested by {self.user.username})"

    class Meta:
        verbose_name_plural = 'Book requests'

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at:%Y-%m-%d %H:%M})"

    class Meta:
        verbose_name_plural = 'Contact messages'
