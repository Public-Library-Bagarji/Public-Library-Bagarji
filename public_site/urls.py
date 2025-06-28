from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from .views import delete_account, PublicSiteLoginView, verify_otp
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('blogs/', views.blogs, name='blogs'),
    path('book-reviews/', views.book_reviews, name='book_reviews'),
    path('books/', views.books, name='books'),
    path('news/', views.news, name='news'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('login/', PublicSiteLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('blogs/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('book-reviews/<int:review_id>/', views.review_detail, name='review_detail'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('digital-resources/', views.digital_resources, name='digital_resources'),
    path('community-programs/', views.community_programs, name='community_programs'),
    path('profile/', views.profile, name='profile'),
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='account/password_change.html', success_url='/profile/'), name='password_change'),
    path('delete-account/', delete_account, name='delete_account'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),
    path('verify-otp/', verify_otp, name='verify_otp'),
] 