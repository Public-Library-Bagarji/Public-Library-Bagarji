"""
URL configuration for public_library_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from library_admin.views import admin_comments_dashboard
from django.views.generic.base import RedirectView

# Remove these direct imports and definitions as they will be handled by including library_admin.urls
# from library_admin.models import News, Article, Book, BookReview
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.http import Http404

# Remove custom view definitions as they will be in library_admin.views
# def news_list(request):
#     news = News.objects.all().order_by('-publication_date')
#     return render(request, 'news_list.html', {'news': news})

# def news_api(request):
#     news = News.objects.all().order_by('-publication_date')
#     news_list = [{'id': item.id, 'title': item.title, 'content': item.content, 'publication_date': item.publication_date} for item in news]
#     return JsonResponse(news_list, safe=False)

# def articles_api(request):
#     articles = Article.objects.all().order_by('-publication_date')
#     article_list = [{'id': article.id, 'title': article.title, 'content': article.content, 'author': article.author, 'publication_date': article.publication_date} for article in articles]
#     return JsonResponse(article_list, safe=False)

# def books_api(request):
#     books = Book.objects.all().order_by('-publication_date')
#     book_list = [{'id': book.id, 'title': book.title, 'author': book.author, 'description': book.description, 'publication_date': book.publication_date, 'cover_image': book.cover_image.url if book.cover_image else None, 'pdf_file': book.pdf_file.url if book.pdf_file else None} for book in books]
#     return JsonResponse(book_list, safe=False)

# def bookreviews_api(request):
#     reviews = BookReview.objects.all().order_by('-review_date')
#     review_list = [{'id': review.id, 'book_title': review.book.title, 'reviewer_name': review.reviewer_name, 'rating': review.rating, 'review_text': review.review_text, 'review_date': review.review_date} for review in reviews]
#     return JsonResponse(review_list, safe=False)

# @csrf_exempt
# def book_detail_api(request, book_id):
#     try:
#         book = Book.objects.get(id=book_id)
#     except Book.DoesNotExist:
#         raise Http404('Book not found')
#     data = {
#         'id': book.id,
#         'title': book.title,
#         'author': book.author,
#         'description': book.description,
#         'publication_date': book.publication_date,
#         'cover_image': book.cover_image.url if book.cover_image else None,
#         'pdf_file': book.pdf_file.url if book.pdf_file else None,
#     }
#     return JsonResponse(data)

# @csrf_exempt
# def article_detail_api(request, article_id):
#     try:
#         article = Article.objects.get(id=article_id)
#     except Article.DoesNotExist:
#         raise Http404('Article not found')
#     data = {
#         'id': article.id,
#         'title': article.title,
#         'content': article.content,
#         'author': article.author,
#         'publication_date': article.publication_date,
#     }
#     return JsonResponse(data)

# @csrf_exempt
# def news_detail_api(request, news_id):
#     try:
#         news = News.objects.get(id=news_id)
#     except News.DoesNotExist:
#         raise Http404('News not found')
#     data = {
#         'id': news.id,
#         'title': news.title,
#         'content': news.content,
#         'publication_date': news.publication_date,
#     }
#     return JsonResponse(data)

# @csrf_exempt
# def bookreview_detail_api(request, review_id):
#     try:
#         review = BookReview.objects.get(id=review_id)
#     except BookReview.DoesNotExist:
#         raise Http404('Review not found')
#     data = {
#         'id': review.id,
#         'book_title': review.book.title,
#         'reviewer_name': review.reviewer_name,
#         'rating': review.rating,
#         'review_text': review.review_text,
#         'review_date': review.review_date,
#     }
#     return JsonResponse(data)

# def book_detail(request, book_id):
#     return render(request, 'book_detail.html', {'book_id': book_id})

urlpatterns = [
    path('admin/comments/', admin_comments_dashboard, name='admin_comments_dashboard'),
    path('admin/', admin.site.urls),
    # Include URLs from the public_site app
    path('', include('public_site.urls')),
    # Include URLs from the library_admin app
    path('', include('library_admin.urls')),
    path('accounts/login/', RedirectView.as_view(url='/login/', permanent=True)),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
