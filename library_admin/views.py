from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from .models import Article, BookReview, Book, News, CommentReply
from comments.models import BlogComment, BookReviewComment, NewsComment, BookComment
from datetime import datetime
from django.db.models import Q
from django.views.decorators.http import require_http_methods, require_POST
import json
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.urls import reverse
from django.urls import reverse_lazy
from django.urls import reverse
from django.urls import reverse_lazy
from functools import wraps
import re
from django.contrib.admin.models import LogEntry, DELETION
from django.contrib.contenttypes.models import ContentType
from public_site.models import UserProfile
from django.conf import settings
from django.db import models

# Create your views here.

def clean_markdown_preview(text):
    """Clean markdown symbols from text for preview purposes"""
    if not text:
        return ""
    
    # Remove markdown symbols
    cleaned = text
    cleaned = re.sub(r'#{1,6}\s+', '', cleaned)  # Remove headers
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)  # Remove bold
    cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)  # Remove italic
    cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cleaned)  # Remove links
    cleaned = re.sub(r'`([^`]+)`', r'\1', cleaned)  # Remove inline code
    cleaned = re.sub(r'^\s*[-*+]\s+', '', cleaned, flags=re.MULTILINE)  # Remove list markers
    cleaned = re.sub(r'^\s*\d+\.\s+', '', cleaned, flags=re.MULTILINE)  # Remove numbered list markers
    cleaned = re.sub(r'\n+', ' ', cleaned)  # Replace multiple newlines with space
    cleaned = re.sub(r'\s+', ' ', cleaned)  # Replace multiple spaces with single space
    
    return cleaned.strip()

def flatten_replies_for_api(comment, parent=None):
    flat = []
    for reply in comment.replies.all().order_by('date'):
        # Determine parent_name: immediate parent (could be user or name field)
        if getattr(reply, 'parent_is_admin_reply', False):
            parent_name = 'Admin'
        elif parent:
            parent_name = parent.user.username if getattr(parent, 'user', None) and parent.user else parent.name
        else:
            parent_name = comment.user.username if getattr(comment, 'user', None) and comment.user else comment.name
        # Build reply dict with parent_name
        reply_dict = {
            'id': reply.id,
            'name': reply.user.username if reply.user else reply.name,
            'comment': reply.comment,
            'rating': reply.rating,
            'date': reply.date.strftime('%Y-%m-%d %H:%M'),
            'profile_image': reply.user.userprofile.profile_image.url if reply.user and hasattr(reply.user, 'userprofile') and reply.user.userprofile.profile_image else '/static/images/default-avatar.png',
            'parent_name': parent_name
        }
        flat.append(reply_dict)
        flat.extend(flatten_replies_for_api(reply, parent=reply))
    return flat

@csrf_exempt
def articles_api(request):
    articles = Article.objects.all().order_by('-publication_date')
    article_list = [{
        'id': article.id,
        'title': article.title,
        'content': clean_markdown_preview(article.content),  # Clean content for preview
        'author': {'name': article.author},
        'created_at': article.publication_date.isoformat(),
        'category': article.category.name if article.category else 'Uncategorized',
        'image': article.image.url if article.image else '/static/images/blog-default.jpg'
    } for article in articles]
    return JsonResponse(article_list, safe=False)

@csrf_exempt
def article_detail_api(request, article_id):
    try:
        article = Article.objects.get(id=article_id)
        data = {
            'id': article.id,
            'title': article.title,
            'content': article.content,
            'author': {'name': article.author},
            'created_at': article.publication_date.isoformat(),
            'category': article.category.name if article.category else 'Uncategorized',
            'image': article.image.url if article.image else '/static/images/blog-default.jpg'
        }
        return JsonResponse(data)
    except Article.DoesNotExist:
        return JsonResponse({'error': 'Article not found'}, status=404)

@csrf_exempt
def bookreviews_api(request):
    category = request.GET.get('category', 'all').lower()
    sort_by = request.GET.get('sort_by', 'newest')

    reviews = BookReview.objects.all()

    if category != 'all':
        reviews = reviews.filter(book__category__iexact=category)

    # Apply sorting
    if sort_by == 'oldest':
        reviews = reviews.order_by('review_date')
    elif sort_by == 'alphabetical':
        reviews = reviews.order_by('book__title') # Sort by book title for alphabetical
    else: # newest
        reviews = reviews.order_by('-review_date')

    review_list = [{
        'id': review.id,
        'book_title': review.book.title,
        'reviewer_name': review.reviewer_name,
        'review_text': clean_markdown_preview(review.review_text),  # Clean review text for preview
        'rating': review.rating,
        'review_date': review.review_date.isoformat(),
        'category': review.book.category, # Include book category in response
        'image': review.image.url if review.image else '/static/images/blog-default.jpg'
    } for review in reviews]
    return JsonResponse(review_list, safe=False)

@csrf_exempt
def bookreview_detail_api(request, review_id):
    try:
        review = BookReview.objects.get(id=review_id)
        data = {
            'id': review.id,
            'book_title': review.book.title,
            'reviewer_name': review.reviewer_name,
            'review_text': review.review_text,
            'rating': review.rating,
            'review_date': review.review_date.isoformat(),
        }
        return JsonResponse(data)
    except BookReview.DoesNotExist:
        return JsonResponse({'error': 'Review not found'}, status=404)

@csrf_exempt
def bookreviews_search_api(request):
    query = request.GET.get('query', '')
    category = request.GET.get('category', 'all').lower()
    sort_by = request.GET.get('sort_by', 'newest')
    print(f"Received search query: '{query}'") # Debug print
    reviews = BookReview.objects.all()

    if category != 'all':
        reviews = reviews.filter(book__category__iexact=category)

    if query:
        reviews = reviews.filter(Q(book__title__icontains=query) | Q(review_text__icontains=query) | Q(reviewer_name__icontains=query))
    
    # Apply sorting
    if sort_by == 'oldest':
        reviews = reviews.order_by('review_date')
    elif sort_by == 'alphabetical':
        reviews = reviews.order_by('book__title') # Sort by book title for alphabetical
    else: # newest
        reviews = reviews.order_by('-review_date')

    print(f"Found {reviews.count()} reviews for query: '{query}'") # Debug print
    review_list = [{
        'id': review.id,
        'book_title': review.book.title,
        'reviewer_name': review.reviewer_name,
        'review_text': clean_markdown_preview(review.review_text),  # Clean review text for preview
        'rating': review.rating,
        'review_date': review.review_date.isoformat(),
        'category': review.book.category # Include book category in response
    } for review in reviews]
    return JsonResponse(review_list, safe=False)

@csrf_exempt
def news_api(request):
    category = request.GET.get('category', 'all').lower()
    sort_by = request.GET.get('sort_by', 'newest')

    news = News.objects.all()

    if category != 'all':
        news = news.filter(category__iexact=category)

    # Apply sorting
    if sort_by == 'oldest':
        news = news.order_by('publication_date')
    elif sort_by == 'alphabetical':
        news = news.order_by('title')
    else: # newest
        news = news.order_by('-publication_date')

    news_list = [{
        'id': item.id,
        'title': item.title,
        'content': clean_markdown_preview(item.content),  # Clean content for preview
        'publication_date': item.publication_date.strftime('%Y-%m-%d'),
        'views': getattr(item, 'views', 0),
        'category': item.category,
        'image': item.image.url if item.image else '/static/images/blog-default.jpg'
    } for item in news]
    return JsonResponse(news_list, safe=False)

@csrf_exempt
def news_detail_api(request, news_id):
    try:
        news = News.objects.get(id=news_id)
        data = {
            'id': news.id,
            'title': news.title,
            'content': news.content,
            'publication_date': news.publication_date.strftime('%Y-%m-%d'),
            'views': getattr(news, 'views', 0)
        }
        return JsonResponse(data)
    except News.DoesNotExist:
        return JsonResponse({'error': 'News not found'}, status=404)

@csrf_exempt
def news_search_api(request):
    query = request.GET.get('query', '').lower()
    category = request.GET.get('category', 'all').lower()
    sort_by = request.GET.get('sort_by', 'newest')

    news = News.objects.all()

    if category != 'all':
        news = news.filter(category__iexact=category)

    if query:
        news = news.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
    
    if sort_by == 'oldest':
        news = news.order_by('publication_date')
    elif sort_by == 'alphabetical':
        news = news.order_by('title')
    else:
        news = news.order_by('-publication_date')
    
    news_list = [{
        'id': item.id,
        'title': item.title,
        'content': clean_markdown_preview(item.content),  # Clean content for preview
        'publication_date': item.publication_date.strftime('%Y-%m-%d'),
        'views': getattr(item, 'views', 0),
        'category': item.category,
        'image': item.image.url if item.image else '/static/images/blog-default.jpg'
    } for item in news]
    return JsonResponse(news_list, safe=False)

@csrf_exempt
def books_api(request):
    category = request.GET.get('category', 'all').lower()
    sort_by = request.GET.get('sort_by', 'newest')

    books = Book.objects.all()

    if category != 'all':
        books = books.filter(category__name__iexact=category)

    if sort_by == 'oldest':
        books = books.order_by('publication_date')
    elif sort_by == 'alphabetical':
        books = books.order_by('title')
    else:
        books = books.order_by('-publication_date')

    book_list = [{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'description': book.description,
        'publication_date': book.publication_date.strftime('%Y-%m-%d') if book.publication_date else None,
        'cover_image': request.build_absolute_uri(book.cover_image.url) if book.cover_image else '/static/images/default-book.jpg',
        'pdf_file': request.build_absolute_uri(book.pdf_file.url) if book.pdf_file else None,
        'views': getattr(book, 'views', 0),
        'category': book.category.name if book.category else None
    } for book in books]
    return JsonResponse(book_list, safe=False)

@csrf_exempt
def book_detail_api(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
        data = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'description': book.description,
            'publication_date': book.publication_date.strftime('%Y-%m-%d') if book.publication_date else None,
            'cover_image': request.build_absolute_uri(book.cover_image.url) if book.cover_image else '/static/images/default-book.jpg',
            'pdf_file': request.build_absolute_uri(book.pdf_file.url) if book.pdf_file else None,
            'views': getattr(book, 'views', 0)
        }
        return JsonResponse(data)
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)

@csrf_exempt
def books_search_api(request):
    query = request.GET.get('query', '').lower()
    category = request.GET.get('category', 'all').lower()
    sort_by = request.GET.get('sort_by', 'newest')

    books = Book.objects.all()

    if category != 'all':
        books = books.filter(category__name__iexact=category)

    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__icontains=query) | Q(description__icontains=query)
        )
    
    if sort_by == 'oldest':
        books = books.order_by('publication_date')
    elif sort_by == 'alphabetical':
        books = books.order_by('title')
    else:
        books = books.order_by('-publication_date')
    
    book_list = [{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'description': book.description,
        'publication_date': book.publication_date.strftime('%Y-%m-%d') if book.publication_date else None,
        'cover_image': request.build_absolute_uri(book.cover_image.url) if book.cover_image else '/static/images/default-book.jpg',
        'pdf_file': request.build_absolute_uri(book.pdf_file.url) if book.pdf_file else None,
        'category': book.category.name if book.category else None
    } for book in books]
    return JsonResponse(book_list, safe=False)

@csrf_exempt
@require_http_methods(["GET", "POST", "PATCH"])
def article_comments_api(request, article_id):
    if request.method == "GET":
        try:
            article = Article.objects.get(id=article_id)
            comments = article.comments.filter(is_active=True, parent__isnull=True).prefetch_related(
                models.Prefetch('replies', queryset=BlogComment.objects.filter(is_active=True).order_by('date'))
            )
            def serialize_comment_flat(comment):
                admin_replies = CommentReply.objects.filter(
                    comment_id=comment.id,
                    comment_type='blog',
                    is_active=True
                ).order_by('date')
                flat_user_replies = flatten_replies_for_api(comment)
                return {
                    'id': comment.id,
                    'name': comment.user.username if comment.user else comment.name,
                    'comment': comment.comment,
                    'rating': comment.rating,
                    'date': comment.date.strftime('%Y-%m-%d %H:%M'),
                    'profile_image': comment.user.userprofile.profile_image.url if comment.user and hasattr(comment.user, 'userprofile') and comment.user.userprofile.profile_image else '/static/images/default-avatar.png',
                    'replies': flat_user_replies,
                    'admin_replies': [{
                        'reply': r.reply,
                        'admin_name': r.admin_name,
                        'date': r.date.strftime('%Y-%m-%d %H:%M')
                    } for r in admin_replies]
                }
            comments_list = [serialize_comment_flat(comment) for comment in comments]
            return JsonResponse(comments_list, safe=False)
        except Article.DoesNotExist:
            return JsonResponse({'error': 'Article not found'}, status=404)
    elif request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=403)
        body = json.loads(request.body)
        parent_id = body.get('parent_id')
        parent_is_admin_reply = body.get('parent_is_admin_reply', False)
        if parent_id:
            comment = BlogComment.objects.create(
                article_id=article_id,
                user=request.user,
                name=request.user.username,
                comment=body['comment'],
                parent_id=parent_id,
                parent_is_admin_reply=parent_is_admin_reply
            )
        else:
            # This is a top-level comment, require rating
            comment = BlogComment.objects.create(
                article_id=article_id,
                user=request.user,
                name=request.user.username,
                comment=body['comment'],
                rating=body['rating']
            )
        return JsonResponse({'success': True}, status=201)
    elif request.method == "PATCH":
        print('DEBUG PATCH:', request.user, request.body)
        body = json.loads(request.body)
        comment_id = body.get('id')
        new_comment = body.get('comment', '').strip()
        new_rating = body.get('rating')
        if not comment_id or not new_comment:
            print('DEBUG PATCH ERROR: Comment cannot be empty.')
            return JsonResponse({'success': False, 'error': 'Comment cannot be empty.'}, status=400)
        if new_rating is not None:
            try:
                new_rating = int(new_rating)
                if new_rating < 1 or new_rating > 5:
                    print('DEBUG PATCH ERROR: Rating must be between 1 and 5.')
                    return JsonResponse({'success': False, 'error': 'Rating must be between 1 and 5.'}, status=400)
            except Exception as e:
                print('DEBUG PATCH ERROR: Invalid rating.', e)
                return JsonResponse({'success': False, 'error': 'Invalid rating.'}, status=400)
        try:
            comment_obj = BlogComment.objects.get(id=comment_id, article_id=article_id)
            if comment_obj.comment.strip() == new_comment and (new_rating is None or comment_obj.rating == new_rating):
                print('DEBUG PATCH ERROR: No change.')
                return JsonResponse({'success': False, 'error': 'You must change the comment or rating.'}, status=400)
            comment_obj.comment = new_comment
            if new_rating is not None:
                comment_obj.rating = new_rating
            comment_obj.save()
            print('DEBUG PATCH SUCCESS')
            return JsonResponse({'success': True})
        except BlogComment.DoesNotExist:
            print('DEBUG PATCH ERROR: Comment not found.')
            return JsonResponse({'success': False, 'error': 'Comment not found.'}, status=404)
        except Exception as e:
            print('DEBUG PATCH ERROR:', e)
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET", "POST", "PATCH"])
def bookreview_comments_api(request, review_id):
    if request.method == "GET":
        try:
            review = BookReview.objects.get(id=review_id)
            comments = review.comments.filter(is_active=True, parent__isnull=True).prefetch_related(
                models.Prefetch('replies', queryset=BookReviewComment.objects.filter(is_active=True).order_by('date'))
            )
            def serialize_comment_flat(comment):
                admin_replies = CommentReply.objects.filter(
                    comment_id=comment.id,
                    comment_type='bookreview',
                    is_active=True
                ).order_by('date')
                flat_user_replies = flatten_replies_for_api(comment)
                return {
                    'id': comment.id,
                    'name': comment.user.username if comment.user else comment.name,
                    'comment': comment.comment,
                    'rating': comment.rating,
                    'date': comment.date.strftime('%Y-%m-%d %H:%M'),
                    'profile_image': comment.user.userprofile.profile_image.url if comment.user and hasattr(comment.user, 'userprofile') and comment.user.userprofile.profile_image else '/static/images/default-avatar.png',
                    'replies': flat_user_replies,
                    'admin_replies': [{
                        'reply': r.reply,
                        'admin_name': r.admin_name,
                        'date': r.date.strftime('%Y-%m-%d %H:%M')
                    } for r in admin_replies]
                }
            comments_list = [serialize_comment_flat(comment) for comment in comments]
            return JsonResponse(comments_list, safe=False)
        except BookReview.DoesNotExist:
            return JsonResponse({'error': 'Review not found'}, status=404)
    elif request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=403)
        body = json.loads(request.body)
        parent_id = body.get('parent_id')
        parent_is_admin_reply = body.get('parent_is_admin_reply', False)
        if parent_id:
            try:
                parent_comment = BookReviewComment.objects.get(id=parent_id)
                if parent_comment.review_id != int(review_id):
                    return JsonResponse({'success': False, 'error': 'Parent comment does not belong to this review.'}, status=400)
            except BookReviewComment.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Parent comment not found.'}, status=404)
            comment = BookReviewComment.objects.create(
                review_id=review_id,
                user=request.user,
                name=request.user.username,
                comment=body['comment'],
                parent=parent_comment,
                parent_is_admin_reply=parent_is_admin_reply
            )
        else:
            # This is a top-level comment, require rating
            comment = BookReviewComment.objects.create(
                review_id=review_id,
                user=request.user,
                name=request.user.username,
                comment=body['comment'],
                rating=body['rating']
            )
        return JsonResponse({'success': True}, status=201)
    elif request.method == "PATCH":
        print('DEBUG PATCH:', request.user, request.body)
        body = json.loads(request.body)
        comment_id = body.get('id')
        new_comment = body.get('comment', '').strip()
        new_rating = body.get('rating')
        if not comment_id or not new_comment:
            print('DEBUG PATCH ERROR: Comment cannot be empty.')
            return JsonResponse({'success': False, 'error': 'Comment cannot be empty.'}, status=400)
        if new_rating is not None:
            try:
                new_rating = int(new_rating)
                if new_rating < 1 or new_rating > 5:
                    print('DEBUG PATCH ERROR: Rating must be between 1 and 5.')
                    return JsonResponse({'success': False, 'error': 'Rating must be between 1 and 5.'}, status=400)
            except Exception as e:
                print('DEBUG PATCH ERROR: Invalid rating.', e)
                return JsonResponse({'success': False, 'error': 'Invalid rating.'}, status=400)
        try:
            comment_obj = BookReviewComment.objects.get(id=comment_id, review_id=review_id)
            if comment_obj.comment.strip() == new_comment and (new_rating is None or comment_obj.rating == new_rating):
                print('DEBUG PATCH ERROR: No change.')
                return JsonResponse({'success': False, 'error': 'You must change the comment or rating.'}, status=400)
            comment_obj.comment = new_comment
            if new_rating is not None:
                comment_obj.rating = new_rating
            comment_obj.save()
            print('DEBUG PATCH SUCCESS')
            return JsonResponse({'success': True})
        except BookReviewComment.DoesNotExist:
            print('DEBUG PATCH ERROR: Comment not found.')
            return JsonResponse({'success': False, 'error': 'Comment not found.'}, status=404)
        except Exception as e:
            print('DEBUG PATCH ERROR:', e)
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET", "POST", "PATCH"])
def news_comments_api(request, news_id):
    if request.method == "GET":
        try:
            news = News.objects.get(id=news_id)
            comments = news.comments.filter(is_active=True, parent__isnull=True).prefetch_related(
                models.Prefetch('replies', queryset=NewsComment.objects.filter(is_active=True).order_by('date'))
            )
            def serialize_comment_flat(comment):
                admin_replies = CommentReply.objects.filter(
                    comment_id=comment.id,
                    comment_type='news',
                    is_active=True
                ).order_by('date')
                flat_user_replies = flatten_replies_for_api(comment)
                return {
                    'id': comment.id,
                    'name': comment.user.username if comment.user else comment.name,
                    'comment': comment.comment,
                    'rating': comment.rating,
                    'date': comment.date.strftime('%Y-%m-%d %H:%M'),
                    'profile_image': comment.user.userprofile.profile_image.url if comment.user and hasattr(comment.user, 'userprofile') and comment.user.userprofile.profile_image else '/static/images/default-avatar.png',
                    'replies': flat_user_replies,
                    'admin_replies': [{
                        'reply': r.reply,
                        'admin_name': r.admin_name,
                        'date': r.date.strftime('%Y-%m-%d %H:%M')
                    } for r in admin_replies]
                }
            comments_list = [serialize_comment_flat(comment) for comment in comments]
            return JsonResponse(comments_list, safe=False)
        except News.DoesNotExist:
            return JsonResponse({'error': 'News not found'}, status=404)
    elif request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=403)
        body = json.loads(request.body)
        parent_id = body.get('parent_id')
        parent_is_admin_reply = body.get('parent_is_admin_reply', False)
        if parent_id:
            try:
                parent_comment = NewsComment.objects.get(id=parent_id)
                if parent_comment.news_id != int(news_id):
                    return JsonResponse({'success': False, 'error': 'Parent comment does not belong to this news.'}, status=400)
            except NewsComment.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Parent comment not found.'}, status=404)
            comment = NewsComment.objects.create(
                news_id=news_id,
                user=request.user,
                name=request.user.username,
                comment=body['comment'],
                parent=parent_comment,
                parent_is_admin_reply=parent_is_admin_reply
            )
        else:
            # This is a top-level comment, require rating
            comment = NewsComment.objects.create(
                news_id=news_id,
                user=request.user,
                name=request.user.username,
                comment=body['comment'],
                rating=body['rating']
            )
        return JsonResponse({'success': True}, status=201)
    elif request.method == "PATCH":
        print('DEBUG PATCH:', request.user, request.body)
        body = json.loads(request.body)
        comment_id = body.get('id')
        new_comment = body.get('comment', '').strip()
        new_rating = body.get('rating')
        if not comment_id or not new_comment:
            print('DEBUG PATCH ERROR: Comment cannot be empty.')
            return JsonResponse({'success': False, 'error': 'Comment cannot be empty.'}, status=400)
        if new_rating is not None:
            try:
                new_rating = int(new_rating)
                if new_rating < 1 or new_rating > 5:
                    print('DEBUG PATCH ERROR: Rating must be between 1 and 5.')
                    return JsonResponse({'success': False, 'error': 'Rating must be between 1 and 5.'}, status=400)
            except Exception as e:
                print('DEBUG PATCH ERROR: Invalid rating.', e)
                return JsonResponse({'success': False, 'error': 'Invalid rating.'}, status=400)
        try:
            comment_obj = NewsComment.objects.get(id=comment_id, news_id=news_id)
            if comment_obj.comment.strip() == new_comment and (new_rating is None or comment_obj.rating == new_rating):
                print('DEBUG PATCH ERROR: No change.')
                return JsonResponse({'success': False, 'error': 'You must change the comment or rating.'}, status=400)
            comment_obj.comment = new_comment
            if new_rating is not None:
                comment_obj.rating = new_rating
            comment_obj.save()
            print('DEBUG PATCH SUCCESS')
            return JsonResponse({'success': True})
        except NewsComment.DoesNotExist:
            print('DEBUG PATCH ERROR: Comment not found.')
            return JsonResponse({'success': False, 'error': 'Comment not found.'}, status=404)
        except Exception as e:
            print('DEBUG PATCH ERROR:', e)
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET", "POST", "PATCH"])
def book_comments_api(request, book_id):
    if request.method == "GET":
        try:
            book = Book.objects.get(id=book_id)
            comments = book.comments.filter(is_active=True, parent__isnull=True).prefetch_related(
                models.Prefetch('replies', queryset=BookComment.objects.filter(is_active=True).order_by('date'))
            )
            def serialize_comment_flat(comment):
                admin_replies = CommentReply.objects.filter(
                    comment_id=comment.id,
                    comment_type='book',
                    is_active=True
                ).order_by('date')
                flat_user_replies = flatten_replies_for_api(comment)
                return {
                    'id': comment.id,
                    'name': comment.user.username if comment.user else comment.name,
                    'comment': comment.comment,
                    'rating': comment.rating,
                    'date': comment.date.strftime('%Y-%m-%d %H:%M'),
                    'profile_image': comment.user.userprofile.profile_image.url if comment.user and hasattr(comment.user, 'userprofile') and comment.user.userprofile.profile_image else '/static/images/default-avatar.png',
                    'replies': flat_user_replies,
                    'admin_replies': [{
                        'reply': r.reply,
                        'admin_name': r.admin_name,
                        'date': r.date.strftime('%Y-%m-%d %H:%M')
                    } for r in admin_replies]
                }
            comments_list = [serialize_comment_flat(comment) for comment in comments]
            return JsonResponse(comments_list, safe=False)
        except Book.DoesNotExist:
            return JsonResponse({'error': 'Book not found'}, status=404)
    elif request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=403)
        body = json.loads(request.body)
        parent_id = body.get('parent_id')
        parent_is_admin_reply = body.get('parent_is_admin_reply', False)
        if parent_id:
            try:
                parent_comment = BookComment.objects.get(id=parent_id)
                if parent_comment.book_id != int(book_id):
                    return JsonResponse({'success': False, 'error': 'Parent comment does not belong to this book.'}, status=400)
            except BookComment.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Parent comment not found.'}, status=404)
            comment = BookComment.objects.create(
                book_id=book_id,
                user=request.user,
                name=request.user.username,
                comment=body['comment'],
                parent=parent_comment,
                parent_is_admin_reply=parent_is_admin_reply
            )
        else:
            # This is a top-level comment, require rating
            comment = BookComment.objects.create(
                book_id=book_id,
                user=request.user,
                name=request.user.username,
                comment=body['comment'],
                rating=body['rating']
            )
        return JsonResponse({'success': True}, status=201)
    elif request.method == "PATCH":
        print('DEBUG PATCH:', request.user, request.body)
        body = json.loads(request.body)
        comment_id = body.get('id')
        new_comment = body.get('comment', '').strip()
        new_rating = body.get('rating')
        if not comment_id or not new_comment:
            print('DEBUG PATCH ERROR: Comment cannot be empty.')
            return JsonResponse({'success': False, 'error': 'Comment cannot be empty.'}, status=400)
        if new_rating is not None:
            try:
                new_rating = int(new_rating)
                if new_rating < 1 or new_rating > 5:
                    print('DEBUG PATCH ERROR: Rating must be between 1 and 5.')
                    return JsonResponse({'success': False, 'error': 'Rating must be between 1 and 5.'}, status=400)
            except Exception as e:
                print('DEBUG PATCH ERROR: Invalid rating.', e)
                return JsonResponse({'success': False, 'error': 'Invalid rating.'}, status=400)
        try:
            comment_obj = BookComment.objects.get(id=comment_id, book_id=book_id)
            if comment_obj.comment.strip() == new_comment and (new_rating is None or comment_obj.rating == new_rating):
                print('DEBUG PATCH ERROR: No change.')
                return JsonResponse({'success': False, 'error': 'You must change the comment or rating.'}, status=400)
            comment_obj.comment = new_comment
            if new_rating is not None:
                comment_obj.rating = new_rating
            comment_obj.save()
            print('DEBUG PATCH SUCCESS')
            return JsonResponse({'success': True})
        except BookComment.DoesNotExist:
            print('DEBUG PATCH ERROR: Comment not found.')
            return JsonResponse({'success': False, 'error': 'Comment not found.'}, status=404)
        except Exception as e:
            print('DEBUG PATCH ERROR:', e)
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
def comment_replies_api(request):
    comment_id = request.GET.get('comment_id')
    comment_type = request.GET.get('comment_type')
    replies = CommentReply.objects.filter(comment_id=comment_id, comment_type=comment_type).order_by('date')
    reply_list = [{
        'id': reply.id,
        'reply': reply.reply,
        'admin_name': reply.admin_name,
        'date': reply.date.strftime('%Y-%m-%d %H:%M'),
        'is_active': reply.is_active
    } for reply in replies]
    return JsonResponse({'replies': reply_list})

@staff_member_required
def admin_comments_dashboard(request):
    blog_comments = BlogComment.objects.all()
    book_comments = BookComment.objects.all()
    bookreview_comments = BookReviewComment.objects.all()
    news_comments = NewsComment.objects.all()
    all_comments = list(blog_comments) + list(book_comments) + list(bookreview_comments) + list(news_comments)
    all_comments.sort(key=lambda c: c.date, reverse=True)

    # Attach admin reply count and flat user reply count to each comment
    for c in all_comments:
        comment_type = None
        if hasattr(c, 'article_id'):
            comment_type = 'blog'
        elif hasattr(c, 'book_id'):
            comment_type = 'book'
        elif hasattr(c, 'review_id'):
            comment_type = 'bookreview'
        elif hasattr(c, 'news_id'):
            comment_type = 'news'
        
        if comment_type:
            c.admin_reply_count = CommentReply.objects.filter(comment_type=comment_type, comment_id=c.id).count()
        else:
            c.admin_reply_count = 0
        c.flat_user_reply_count = flatten_replies_count(c)

    context = {
        'comments': all_comments,
    }
    return render(request, "admin/comments_changelist.html", context)

def flatten_replies_count(comment):
    count = comment.replies.count()
    for reply in comment.replies.all():
        count += flatten_replies_count(reply)
    return count

def staff_member_required_json(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            # Always return JSON error for this endpoint
            return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@csrf_exempt
@require_POST
@staff_member_required_json
def admin_reply_comment(request):
    try:
        import json
        data = json.loads(request.body)
        print('DATA:', data)  # Debug print
        reply = data.get('reply')
        comment_id = data.get('comment_id')
        comment_type = data.get('comment_type')
        admin_name = request.user.get_username() if request.user.is_authenticated else 'admin'
        CommentReply.objects.create(
            comment_type=comment_type,
            comment_id=int(comment_id),  # Ensure integer
            reply=reply,
            admin_name=admin_name
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_POST
@staff_member_required_json
def admin_delete_comment(request):
    import json
    from django.http import JsonResponse
    data = json.loads(request.body)
    comment_id = data.get('comment_id')
    comment_type = data.get('comment_type')
    if not comment_id or not comment_type:
        return JsonResponse({'success': False, 'error': 'Missing comment id or type.'}, status=400)
    try:
        if comment_type == 'blog':
            from .models import BlogComment
            obj = BlogComment.objects.get(id=comment_id)
        elif comment_type == 'book':
            from .models import BookComment
            obj = BookComment.objects.get(id=comment_id)
        elif comment_type == 'bookreview':
            from .models import BookReviewComment
            obj = BookReviewComment.objects.get(id=comment_id)
        elif comment_type == 'news':
            from .models import NewsComment
            obj = NewsComment.objects.get(id=comment_id)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid comment type.'}, status=400)
        obj_repr = str(obj)
        obj_pk = obj.pk
        obj.delete()
        # Log the deletion for admin recent actions
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(obj).pk,
            object_id=obj_pk,
            object_repr=obj_repr,
            action_flag=DELETION,
            change_message="Deleted via custom admin dashboard"
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_POST
@staff_member_required_json
def edit_admin_reply(request):
    """
    Edits the text of an admin reply.
    """
    try:
        data = json.loads(request.body)
        reply_id = data.get('reply_id')
        new_text = data.get('text', '').strip()

        if not reply_id or not new_text:
            return JsonResponse({'success': False, 'error': 'Reply ID or text not provided'}, status=400)

        reply = CommentReply.objects.get(id=reply_id)
        reply.reply = new_text
        reply.save()
        
        return JsonResponse({'success': True, 'new_text': new_text})
    except CommentReply.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Admin reply not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_POST
@staff_member_required_json
def toggle_admin_reply_visibility(request):
    """
    Toggles the is_active status of an admin reply (CommentReply).
    """
    try:
        data = json.loads(request.body)
        reply_id = data.get('reply_id')
        if not reply_id:
            return JsonResponse({'success': False, 'error': 'Reply ID not provided'}, status=400)
            
        reply = CommentReply.objects.get(id=reply_id)
        reply.is_active = not reply.is_active
        reply.save()
        
        return JsonResponse({'success': True, 'is_active': reply.is_active})
    except CommentReply.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Admin reply not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_POST
@staff_member_required_json
def delete_admin_reply(request):
    """
    Deletes an admin reply (CommentReply object).
    """
    try:
        data = json.loads(request.body)
        reply_id = data.get('reply_id')
        if not reply_id:
            return JsonResponse({'success': False, 'error': 'Reply ID not provided'}, status=400)
            
        reply = CommentReply.objects.get(id=reply_id)
        reply.delete()
        
        return JsonResponse({'success': True})
    except CommentReply.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Admin reply not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@staff_member_required
def get_user_replies(request):
    comment_id = request.GET.get('comment_id')
    comment_type = request.GET.get('comment_type')

    model_map = {
        'blog': BlogComment,
        'book': BookComment,
        'bookreview': BookReviewComment,
        'news': NewsComment,
    }

    model = model_map.get(comment_type)
    if not model or not comment_id:
        return JsonResponse({'error': 'Invalid parameters'}, status=400)

    try:
        parent_comment = model.objects.get(id=comment_id)
        replies = flatten_replies_for_api(parent_comment)
        reply_list = [{
            'id': reply.id,
            'user': reply.user.username if reply.user else 'Anonymous',
            'comment': reply.comment,
            'date': reply.date.strftime('%Y-%m-%d %H:%M'),
            'is_active': reply.is_active
        } for reply in replies]
        return JsonResponse({'replies': reply_list})
    except model.DoesNotExist:
        return JsonResponse({'error': 'Parent comment not found'}, status=404)

@require_POST
@staff_member_required_json
def toggle_comment_visibility(request):
    """
    Toggles the is_active status of a given comment or reply.
    """
    try:
        data = json.loads(request.body)
        comment_id = data.get('comment_id')
        comment_type = data.get('comment_type')

        model_map = {
            'blog': BlogComment,
            'book': BookComment,
            'bookreview': BookReviewComment,
            'news': NewsComment,
        }
        
        model = model_map.get(comment_type)
        if not model or not comment_id:
            return JsonResponse({'success': False, 'error': 'Invalid parameters'}, status=400)

        comment = model.objects.get(id=comment_id)
        comment.is_active = not comment.is_active
        comment.save()
        
        return JsonResponse({'success': True, 'is_active': comment.is_active})
    except (model.DoesNotExist, AttributeError):
        return JsonResponse({'success': False, 'error': 'Comment not found or invalid type'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
def blogs_api(request):
    category = request.GET.get('category', 'all')
    sort_by = request.GET.get('sort', 'newest')

    blogs = Article.objects.all()
    if category != 'all':
        blogs = blogs.filter(category__name__iexact=category)

    if sort_by == 'oldest':
        blogs = blogs.order_by('publication_date')
    elif sort_by == 'alphabetical':
        blogs = blogs.order_by('title')
    else:
        blogs = blogs.order_by('-publication_date')

    blog_list = [{
        'id': blog.id,
        'title': blog.title,
        'content': blog.content[:200],
        'image_url': blog.image.url if blog.image else '/static/images/blog-default.jpg',
        'category': blog.category.name if blog.category else '',
    } for blog in blogs]
    return JsonResponse(blog_list, safe=False)

@csrf_exempt
def bookreviews_list_api(request):
    category = request.GET.get('category', 'all')
    sort_by = request.GET.get('sort', 'newest')

    reviews = BookReview.objects.all()
    if category != 'all':
        reviews = reviews.filter(book__category__iexact=category)

    if sort_by == 'oldest':
        reviews = reviews.order_by('review_date')
    elif sort_by == 'alphabetical':
        reviews = reviews.order_by('book__title')
    else:
        reviews = reviews.order_by('-review_date')

    review_list = [{
        'id': review.id,
        'book_title': review.book.title,
        'reviewer_name': review.reviewer_name,
        'review_text': review.review_text[:200],
        'rating': review.rating,
        'review_date': review.review_date.isoformat(),
        'category': review.book.category,
        'image_url': review.image.url if review.image else '/static/images/blog-default.jpg',
    } for review in reviews]
    return JsonResponse(review_list, safe=False)

@csrf_exempt
def books_suggestions_api(request):
    query = request.GET.get('q', '').strip()
    suggestions = []
    if query:
        books = Book.objects.filter(title__icontains=query).order_by('title')[:8]
        suggestions = list(books.values_list('title', flat=True))
    return JsonResponse({'suggestions': suggestions})

@csrf_exempt
@require_POST
@staff_member_required_json
def delete_user_reply(request):
    import json
    data = json.loads(request.body)
    reply_id = data.get('reply_id')
    comment_type = data.get('comment_type')
    if not reply_id or not comment_type:
        return JsonResponse({'success': False, 'error': 'Missing reply id or type.'}, status=400)
    model_map = {
        'blog': BlogComment,
        'book': BookComment,
        'bookreview': BookReviewComment,
        'news': NewsComment,
    }
    model = model_map.get(comment_type)
    if not model:
        return JsonResponse({'success': False, 'error': 'Invalid comment type.'}, status=400)
    try:
        reply = model.objects.get(id=reply_id)
        reply.delete()
        return JsonResponse({'success': True})
    except model.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Reply not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
