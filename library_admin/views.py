from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from .models import Article, BookReview, Book, News, BlogComment, BookReviewComment, NewsComment, BookComment, CommentReply
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
        books = books.filter(category__iexact=category)

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
        'category': book.category
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
        books = books.filter(category__iexact=category)

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
        'views': getattr(book, 'views', 0),
        'category': book.category
    } for book in books]
    return JsonResponse(book_list, safe=False)

@csrf_exempt
@require_http_methods(["GET", "POST", "PATCH"])
def article_comments_api(request, article_id):
    if request.method == "GET":
        comments = BlogComment.objects.filter(article_id=article_id).order_by('-date')
        data = []
        for c in comments:
            replies = CommentReply.objects.filter(comment_type='blog', comment_id=c.id).order_by('date')
            profile_image = '/static/images/default_profile.png'
            if c.user_id:
                try:
                    profile = UserProfile.objects.get(user_id=c.user_id)
                    if profile.profile_image:
                        profile_image = profile.profile_image.url
                except UserProfile.DoesNotExist:
                    pass
            data.append({
                'id': c.id,
                'name': c.name,
                'comment': c.comment,
                'rating': c.rating,
                'date': c.date.strftime('%Y-%m-%d %H:%M'),
                'profile_image': profile_image,
                'is_owner': request.user.is_authenticated and c.user_id == request.user.id,
                'replies': [
                    {
                        'reply': r.reply,
                        'admin_name': r.admin_name,
                        'date': r.date.strftime('%Y-%m-%d %H:%M'),
                        'admin_image': '/static/images/websitemainlogo.jpg'
                    } for r in replies
                ]
            })
        return JsonResponse(data, safe=False)
    elif request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=403)
        body = json.loads(request.body)
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

# @csrf_exempt
# @require_http_methods(["DELETE"])
# def delete_article_comment(request, article_id, comment_id):
#     try:
#         comment = BlogComment.objects.get(id=comment_id, article_id=article_id)
#         comment.delete()
#         return JsonResponse({'success': True})
#     except BlogComment.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Comment not found'}, status=404)
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET", "POST", "PATCH"])
def bookreview_comments_api(request, review_id):
    if request.method == "GET":
        comments = BookReviewComment.objects.filter(review_id=review_id).order_by('-date')
        data = []
        for c in comments:
            replies = CommentReply.objects.filter(comment_type='bookreview', comment_id=c.id).order_by('date')
            profile_image = '/static/images/default_profile.png'
            if c.user_id:
                try:
                    profile = UserProfile.objects.get(user_id=c.user_id)
                    if profile.profile_image:
                        profile_image = profile.profile_image.url
                except UserProfile.DoesNotExist:
                    pass
            data.append({
                'id': c.id,
                'name': c.name,
                'comment': c.comment,
                'rating': c.rating,
                'date': c.date.strftime('%Y-%m-%d %H:%M'),
                'profile_image': profile_image,
                'is_owner': request.user.is_authenticated and c.user_id == request.user.id,
                'replies': [
                    {
                        'reply': r.reply,
                        'admin_name': r.admin_name,
                        'date': r.date.strftime('%Y-%m-%d %H:%M'),
                        'admin_image': '/static/images/websitemainlogo.jpg'
                    } for r in replies
                ]
            })
        return JsonResponse(data, safe=False)
    elif request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=403)
        body = json.loads(request.body)
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

# @csrf_exempt
# @require_http_methods(["DELETE"])
# def delete_bookreview_comment(request, review_id, comment_id):
#     try:
#         comment = BookReviewComment.objects.get(id=comment_id, review_id=review_id)
#         comment.delete()
#         return JsonResponse({'success': True})
#     except BookReviewComment.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Comment not found'}, status=404)
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET", "POST", "PATCH"])
def news_comments_api(request, news_id):
    if request.method == "GET":
        comments = NewsComment.objects.filter(news_id=news_id).order_by('-date')
        data = []
        for c in comments:
            replies = CommentReply.objects.filter(comment_type='news', comment_id=c.id).order_by('date')
            profile_image = '/static/images/default_profile.png'
            if c.user_id:
                try:
                    profile = UserProfile.objects.get(user_id=c.user_id)
                    if profile.profile_image:
                        profile_image = profile.profile_image.url
                except UserProfile.DoesNotExist:
                    pass
            data.append({
                'id': c.id,
                'name': c.name,
                'comment': c.comment,
                'rating': c.rating,
                'date': c.date.strftime('%Y-%m-%d %H:%M'),
                'profile_image': profile_image,
                'is_owner': request.user.is_authenticated and c.user_id == request.user.id,
                'replies': [
                    {
                        'reply': r.reply,
                        'admin_name': r.admin_name,
                        'date': r.date.strftime('%Y-%m-%d %H:%M'),
                        'admin_image': '/static/images/websitemainlogo.jpg'
                    } for r in replies
                ]
            })
        return JsonResponse(data, safe=False)
    elif request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=403)
        body = json.loads(request.body)
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

# @csrf_exempt
# @require_http_methods(["DELETE"])
# def delete_news_comment(request, news_id, comment_id):
#     try:
#         comment = NewsComment.objects.get(id=comment_id, news_id=news_id)
#         comment.delete()
#         return JsonResponse({'success': True})
#     except NewsComment.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Comment not found'}, status=404)
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET", "POST", "PATCH"])
def book_comments_api(request, book_id):
    if request.method == "GET":
        comments = BookComment.objects.filter(book_id=book_id).order_by('-date')
        data = []
        for c in comments:
            replies = CommentReply.objects.filter(comment_type='book', comment_id=c.id).order_by('date')
            profile_image = '/static/images/default_profile.png'
            if c.user_id:
                try:
                    profile = UserProfile.objects.get(user_id=c.user_id)
                    if profile.profile_image:
                        profile_image = profile.profile_image.url
                except UserProfile.DoesNotExist:
                    pass
            data.append({
                'id': c.id,
                'name': c.name,
                'comment': c.comment,
                'rating': c.rating,
                'date': c.date.strftime('%Y-%m-%d %H:%M'),
                'profile_image': profile_image,
                'is_owner': request.user.is_authenticated and c.user_id == request.user.id,
                'replies': [
                    {
                        'reply': r.reply,
                        'admin_name': r.admin_name,
                        'date': r.date.strftime('%Y-%m-%d %H:%M'),
                        'admin_image': '/static/images/websitemainlogo.jpg'
                    } for r in replies
                ]
            })
        return JsonResponse(data, safe=False)
    elif request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=403)
        body = json.loads(request.body)
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

@staff_member_required
def admin_comments_dashboard(request):
    blog_comments = BlogComment.objects.all()
    book_comments = BookComment.objects.all()
    bookreview_comments = BookReviewComment.objects.all()
    news_comments = NewsComment.objects.all()
    all_comments = list(blog_comments) + list(book_comments) + list(bookreview_comments) + list(news_comments)
    all_comments.sort(key=lambda c: c.date, reverse=True)

    # Attach reply to each comment (if exists)
    for c in all_comments:
        if hasattr(c, 'article_id'):
            c.reply = CommentReply.objects.filter(comment_type='blog', comment_id=c.id).first()
        elif hasattr(c, 'book_id'):
            c.reply = CommentReply.objects.filter(comment_type='book', comment_id=c.id).first()
        elif hasattr(c, 'review_id'):
            c.reply = CommentReply.objects.filter(comment_type='bookreview', comment_id=c.id).first()
        elif hasattr(c, 'news_id'):
            c.reply = CommentReply.objects.filter(comment_type='news', comment_id=c.id).first()
        else:
            c.reply = None

    context = {
        'comments': all_comments,
    }
    return render(request, "admin/comments_changelist.html", context)

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

@csrf_exempt
def comment_replies_api(request):
    if request.method == 'GET':
        comment_id = request.GET.get('comment_id')
        comment_type = request.GET.get('comment_type')
        from .models import CommentReply
        replies = CommentReply.objects.filter(comment_type=comment_type, comment_id=comment_id).order_by('date')
        data = [
            {
                'reply': r.reply,
                'admin_name': r.admin_name,
                'date': r.date.strftime('%Y-%m-%d %H:%M'),
                'admin_image': '/static/images/websitemainlogo.jpg'
            }
            for r in replies
        ]
        return JsonResponse({'replies': data})

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
