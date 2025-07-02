from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField()
    pdf_file = models.FileField(upload_to='book_pdfs/', blank=True, null=True)
    publication_date = models.DateField(null=True, blank=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    available = models.BooleanField(default=True)
    category = models.ForeignKey('Category', on_delete=models.PROTECT, blank=False, null=False, related_name='books')
    history = HistoricalRecords()

    def __str__(self):
        return self.title

class Category(models.Model):
    TYPE_CHOICES = [
        ('book', 'Book'),
        ('blog', 'Blog/Article'),
        ('news', 'News'),
    ]
    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='book')
    active = models.BooleanField(default=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=100)
    publication_date = models.DateField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, blank=False, null=False, related_name='articles')
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Blog'
        verbose_name_plural = 'Blogs'

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    publication_date = models.DateField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, blank=False, null=False, related_name='news')
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'News'
        verbose_name_plural = 'News'

class BookReview(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reviewer_name = models.CharField(max_length=100)
    review_text = models.TextField()
    review_date = models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to='review_images/', blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"Review for {self.book.title} by {self.reviewer_name}"

class CommentReply(models.Model):
    COMMENT_TYPE_CHOICES = [
        ('blog', 'Blog'),
        ('book', 'Book'),
        ('bookreview', 'Book Review'),
        ('news', 'News'),
    ]
    comment_type = models.CharField(max_length=20, choices=COMMENT_TYPE_CHOICES)
    comment_id = models.IntegerField()
    reply = models.TextField()
    admin_name = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Reply by {self.admin_name} to {self.comment_type} comment {self.comment_id} [Reply ID: {self.id}]"
