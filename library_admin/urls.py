from django.urls import path
from . import views
from .views import article_comments_api, bookreview_comments_api, blogs_api, bookreviews_list_api, books_suggestions_api

urlpatterns = [
    # ... existing urls ...
    path('api/articles/', views.articles_api, name='articles_api'),
    path('api/articles/<int:article_id>/', views.article_detail_api, name='article_detail_api'),
    path('api/articles/<int:article_id>/comments/', article_comments_api, name='article_comments_api'),
    path('api/bookreviews/', views.bookreviews_api, name='bookreviews_api'),
    path('api/bookreviews/<int:review_id>/', views.bookreview_detail_api, name='bookreview_detail_api'),
    path('api/bookreviews/<int:review_id>/comments/', bookreview_comments_api, name='bookreview_comments_api'),
    path('api/bookreviews/search/', views.bookreviews_search_api, name='bookreviews_search_api'),
    path('api/bookreviews/list/', bookreviews_list_api, name='bookreviews_list_api'),
    # News API endpoints
    path('api/news/', views.news_api, name='news_api'),
    path('api/news/<int:news_id>/', views.news_detail_api, name='news_detail_api'),
    path('api/news/search/', views.news_search_api, name='news_search_api'),
    path('api/news/<int:news_id>/comments/', views.news_comments_api, name='news_comments_api'),
    # Book API endpoints
    path('api/books/', views.books_api, name='books_api'),
    path('api/books/<int:book_id>/', views.book_detail_api, name='book_detail_api'),
    path('api/books/search/', views.books_search_api, name='books_search_api'),
    path('api/books/<int:book_id>/comments/', views.book_comments_api, name='book_comments_api'),
    path('admin/comments/reply/', views.admin_reply_comment, name='admin_reply_comment'),
    path('api/comments/delete/', views.admin_delete_comment, name='api_admin_delete_comment'),
    path('api/comments/reply/', views.admin_reply_comment, name='api_admin_reply_comment'),
    path('api/comments/replies/', views.comment_replies_api, name='comment_replies_api'),
    path('api/blogs/', blogs_api, name='blogs_api'),
    path('api/books/suggestions/', books_suggestions_api, name='books_suggestions_api'),
] 