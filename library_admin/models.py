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
    views = models.IntegerField(default=0)
    category = models.CharField(max_length=100, blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

class Keyword(models.Model):
    word = models.CharField(max_length=50, unique=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.word

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=100)
    publication_date = models.DateField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='articles')
    keywords = models.ManyToManyField(Keyword, blank=True, related_name='articles')
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
    views = models.IntegerField(default=0)
    category = models.CharField(max_length=100, blank=True, null=True)
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
    rating = models.IntegerField()
    review_text = models.TextField()
    review_date = models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to='review_images/', blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"Review for {self.book.title} by {self.reviewer_name}"

class BookReviewComment(models.Model):
    review = models.ForeignKey(BookReview, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    comment = models.TextField()
    rating = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} on {self.review.book.title} review"

class BlogComment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    comment = models.TextField()
    rating = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} on {self.article.title}"

class NewsComment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    comment = models.TextField()
    rating = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} on {self.news.title}"

class BookComment(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    comment = models.TextField()
    rating = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} on {self.book.title}"

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

    def __str__(self):
        return f"Reply by {self.admin_name} to {self.comment_type} comment {self.comment_id}"
