from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from library_admin.models import Article, Book, BookReview, News

# Create your models here.

class BookReviewComment(models.Model):
    review = models.ForeignKey(BookReview, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    comment = models.TextField()
    rating = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    parent_is_admin_reply = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return f"[{self.id}] {self.name} on {self.review.book.title} review"

class BlogComment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    comment = models.TextField()
    rating = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    parent_is_admin_reply = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return f"[{self.id}] {self.name} on {self.article.title}"

class NewsComment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    comment = models.TextField()
    rating = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    parent_is_admin_reply = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return f"[{self.id}] {self.name} on {self.news.title}"

class BookComment(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    comment = models.TextField()
    rating = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    parent_is_admin_reply = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return f"[{self.id}] {self.name} on {self.book.title}"
