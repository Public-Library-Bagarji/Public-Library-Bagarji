from django.shortcuts import render, get_object_or_404
from library_admin.models import Book, Article, News, BookReview, Category
import markdown
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect
from django.db import IntegrityError
from .models import UserProfile
from messages_requests.models import ContactMessage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from itertools import chain
from operator import attrgetter
from django.utils import timezone
import random
from django.core.paginator import Paginator
from library_admin.forms import BookRequestForm

# Create your views here.

def home(request):
    # Fetch latest 5 items for each type
    latest_blogs = Article.objects.order_by('-publication_date')[:5]
    latest_news = News.objects.order_by('-publication_date')[:5]
    latest_reviews = BookReview.objects.order_by('-review_date')[:5]

    # Add extra fields for template compatibility
    for item in latest_blogs:
        item.type = 'blog'
        item.image_url = item.image.url if item.image else '/static/images/blog-default.jpg'
    for item in latest_news:
        item.type = 'news'
        item.image_url = item.image.url if item.image else '/static/images/blog-default.jpg'
    for item in latest_reviews:
        item.type = 'review'
        item.book_title = item.book.title
        item.reviewer_name = item.reviewer_name
        item.image_url = item.image.url if item.image else '/static/images/blog-default.jpg'

    return render(request, 'home.html', {
        'latest_blogs': latest_blogs,
        'latest_news': latest_news,
        'latest_reviews': latest_reviews,
    })

def blogs(request):
    from library_admin.models import Article
    from django.core.paginator import Paginator
    
    # Get filter parameters
    category = request.GET.get('category', 'all')
    sort_by = request.GET.get('sort', 'newest')
    
    # Get all blogs
    blogs = Article.objects.all()
    
    # Apply category filter
    if category != 'all':
        blogs = blogs.filter(category__name__iexact=category)
    
    # Apply sorting
    if sort_by == 'oldest':
        blogs = blogs.order_by('publication_date')
    elif sort_by == 'alphabetical':
        blogs = blogs.order_by('title')
    else:  # newest
        blogs = blogs.order_by('-publication_date')
    
    # Add image_url to each blog
    for item in blogs:
        item.image_url = item.image.url if item.image else '/static/images/blog-default.jpg'
    
    # Pagination - 12 blogs per page
    paginator = Paginator(blogs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all categories for the filter dropdown
    blog_categories = (
        Article.objects.filter(category__isnull=False)
        .values_list('category__name', flat=True).distinct()
    )
    
    return render(request, 'blogs.html', {
        'blogs': page_obj.object_list, 
        'page_obj': page_obj, 
        'blog_categories': blog_categories,
        'django_api_url': request.build_absolute_uri('/').rstrip('/')
    })

def book_reviews(request):
    from library_admin.models import BookReview, Book
    from django.core.paginator import Paginator
    
    # Get filter parameters
    category = request.GET.get('category', 'all')
    sort_by = request.GET.get('sort', 'newest')
    
    # Get all reviews
    reviews = BookReview.objects.all()
    
    # Get categories for the filter dropdown (only active book categories)
    review_categories = Category.objects.filter(type='book', active=True, books__isnull=False).distinct()

    # Apply category filter (by id)
    if category != 'all':
        reviews = reviews.filter(book__category=category)
    
    # Apply sorting
    if sort_by == 'oldest':
        reviews = reviews.order_by('review_date')
    elif sort_by == 'alphabetical':
        reviews = reviews.order_by('book__title')
    else:  # newest
        reviews = reviews.order_by('-review_date')
    
    # Add image_url to each review
    for item in reviews:
        item.image_url = item.image.url if item.image else '/static/images/blog-default.jpg'
    
    # Pagination - 12 reviews per page
    paginator = Paginator(reviews, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'book_reviews.html', {
        'reviews': page_obj.object_list, 
        'page_obj': page_obj, 
        'review_categories': review_categories,
        'django_api_url': request.build_absolute_uri('/').rstrip('/')
    })

def books(request):
    from library_admin.models import Book, Category
    book_categories = (
        Category.objects.filter(type='book', active=True, books__isnull=False)
        .distinct()
        .values_list('name', flat=True)
    )
    book_request_form = None
    book_request_success = False
    if request.user.is_authenticated:
        if request.method == 'POST' and 'book_request_submit' in request.POST:
            form = BookRequestForm(request.POST)
            if form.is_valid():
                book_request = form.save(commit=False)
                book_request.user = request.user
                book_request.save()
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                book_request_success = True
                book_request_form = BookRequestForm()  # Reset form
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
                    return JsonResponse({'success': False, 'errors': errors})
                book_request_form = form
        else:
            book_request_form = BookRequestForm()
    return render(request, 'books.html', {
        'book_categories': book_categories,
        'django_api_url': request.build_absolute_uri('/').rstrip('/'),
        'book_request_form': book_request_form,
        'book_request_success': book_request_success,
    })

def news(request):
    from library_admin.models import News
    from django.core.paginator import Paginator
    
    # Get filter parameters
    category = request.GET.get('category', 'all')
    sort_by = request.GET.get('sort', 'newest')
    
    # Get all news
    news_items = News.objects.all()
    
    # Apply category filter
    if category != 'all':
        news_items = news_items.filter(category__name__iexact=category)
    
    # Apply sorting
    if sort_by == 'oldest':
        news_items = news_items.order_by('publication_date')
    elif sort_by == 'alphabetical':
        news_items = news_items.order_by('title')
    else:  # newest
        news_items = news_items.order_by('-publication_date')
    
    # Pagination - 12 news items per page
    paginator = Paginator(news_items, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all categories for the filter dropdown
    news_categories = (
        News.objects.exclude(category__isnull=True)
        .values_list('category__name', flat=True).distinct()
    )
    
    return render(request, 'news.html', {
        'news': page_obj.object_list, 
        'page_obj': page_obj, 
        'news_categories': news_categories,
        'django_api_url': request.build_absolute_uri('/').rstrip('/')
    })

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            # Optionally, add a success message or redirect
            return render(request, 'contact.html', {'success': True})
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

def custom_login(request):
    return render(request, 'account/login.html')

@login_required
def profile(request):
    # Block superusers and staff from accessing public profile
    if request.user.is_superuser or request.user.is_staff:
        messages.error(request, 'Admins and staff cannot access the public profile page.')
        return redirect('home')
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        # Profile image update
        if 'profile_image' in request.FILES:
            # Delete old image if exists and is not default/static
            if profile.profile_image and profile.profile_image.name:
                old_image_path = profile.profile_image.path
                # Only delete if file exists and is inside MEDIA_ROOT (not a static/default image)
                if os.path.isfile(old_image_path) and str(settings.MEDIA_ROOT) in str(old_image_path):
                    try:
                        os.remove(old_image_path)
                    except Exception as e:
                        print(f"Error deleting old profile image: {e}")
            # Save new image
            profile.profile_image = request.FILES['profile_image']
            profile.save()
            messages.success(request, 'Profile image updated successfully!')
        # Profile info update
        elif 'email' in request.POST or 'phone' in request.POST:
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            if email and email != request.user.email:
                request.user.email = email
                request.user.save()
                messages.success(request, 'Email updated successfully!')
            if phone and phone != profile.phone:
                profile.phone = phone
                profile.save()
                messages.success(request, 'Phone updated successfully!')
    return render(request, 'account/profile.html', {'profile': profile})

@login_required
@csrf_exempt
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('home')
    return redirect('profile')

signer = TimestampSigner()

def register(request):
    # Clean up orphaned UserProfiles (no related user)
    from public_site.models import UserProfile
    UserProfile.objects.filter(user__isnull=True).delete()
    email_error = None
    username_error = None
    password_error = None
    phone_error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender', 'male')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if not phone:
            phone_error = 'Phone number is required.'
        if password1 != password2:
            password_error = 'Passwords do not match.'
        if User.objects.filter(email=email, is_active=True).exists():
            email_error = 'This email is already registered.'
        if User.objects.filter(username=username, is_active=True).exists():
            username_error = 'This username is already taken.'
        if email_error or username_error or password_error or phone_error:
            return render(request, 'account/signup.html', {
                'email_error': email_error,
                'username_error': username_error,
                'password_error': password_error,
                'phone_error': phone_error,
                'username': username,
                'email': email,
                'phone': phone,
                'gender': gender,
            })
        # Check for existing inactive user by username or email
        inactive_user = User.objects.filter(username=username, is_active=False).first()
        if not inactive_user:
            inactive_user = User.objects.filter(email=email, is_active=False).first()
        if inactive_user:
            # If the inactive user has a blank username, set it
            if not inactive_user.username:
                inactive_user.username = username
            if not inactive_user.email:
                inactive_user.email = email
            inactive_user.set_password(password1)
            # If still blank, delete and create new
            if not inactive_user.username:
                inactive_user.delete()
                user = User.objects.create_user(username=username, email=email, password=password1, is_active=False)
                if not user.is_superuser and not user.is_staff:
                    UserProfile.objects.create(user=user, phone=phone, gender=gender)
            else:
                inactive_user.save()
                user = inactive_user
                # Update or create UserProfile only for non-staff, non-superuser
                if not user.is_superuser and not user.is_staff:
                    profile, _ = UserProfile.objects.get_or_create(user=user)
                    profile.phone = phone
                    profile.gender = gender
                    profile.save()
        else:
            user = User.objects.create_user(username=username, email=email, password=password1, is_active=False)
            if not user.is_superuser and not user.is_staff:
                UserProfile.objects.create(user=user, phone=phone, gender=gender)
        # Generate OTP
        otp_code = str(random.randint(100000, 999999))
        from public_site.models import EmailOTP
        EmailOTP.objects.update_or_create(user=user, defaults={'code': otp_code, 'is_verified': False})
        # Send OTP email
        subject = 'Your OTP Code - Public Library Bagarji'
        from_email = 'Public Library Bagarji <kaleemullahchanna786@gmail.com>'
        to_email = email
        context = {
            'user': user,
            'otp_code': otp_code,
            'domain': f"http://{get_current_site(request).domain}",
            'now': timezone.now(),
        }
        html_content = render_to_string('account/otp_email.html', context)
        text_content = f"Hi {user.username},\n\nYour OTP code is: {otp_code}\n\nEnter this code on the website to verify your account."
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        # Store registration info in session for OTP verification
        request.session['pending_username'] = username
        request.session['pending_password'] = password1
        request.session['pending_email'] = email
        # Render OTP input page
        return render(request, 'account/verify_otp.html', {'email': email})
    return render(request, 'account/signup.html')

@csrf_exempt
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        # Validate token (valid for 1 day)
        signer.unsign(token, max_age=60*60*24)
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated! You can now log in.')
        return redirect('login')
    except (User.DoesNotExist, BadSignature, SignatureExpired):
        messages.error(request, 'Activation link is invalid or expired.')
        return redirect('login')

def blog_detail(request, blog_id):
    blog = get_object_or_404(Article, id=blog_id)
    blog.content = markdown.markdown(blog.content, extensions=["extra", "codehilite", "toc"])
    # Get related blogs (e.g., same category, excluding current blog)
    related_blogs = Article.objects.filter(category=blog.category).exclude(id=blog.id)[:6] if blog.category else Article.objects.exclude(id=blog.id)[:6]
    return render(request, 'blog_detail.html', {'blog': blog, 'blog_id': blog_id, 'blogs': related_blogs})

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.description = markdown.markdown(book.description, extensions=["extra", "codehilite", "toc"])
    return render(request, 'book_detail.html', {'book': book})

def review_detail(request, review_id):
    review = get_object_or_404(BookReview, id=review_id)
    review.review_text = markdown.markdown(review.review_text, extensions=["extra", "codehilite", "toc"])
    return render(request, 'book_review_detail.html', {'review': review, 'review_id': review_id})

def news_detail(request, news_id):
    news = get_object_or_404(News, id=news_id)
    news.content = markdown.markdown(news.content, extensions=["extra", "codehilite", "toc"])
    return render(request, 'news_detail.html', {'news': news})

def digital_resources(request):
    """Digital Resources page with information about online resources"""
    digital_resources_data = {
        'e_books': {
            'title': 'E-Books Collection',
            'description': 'Access thousands of digital books from our online library',
            'icon': 'fas fa-tablet-alt',
            'features': ['PDF Downloads', 'Online Reading', 'Mobile Compatible', 'Offline Access']
        },
        'audiobooks': {
            'title': 'Audiobooks',
            'description': 'Listen to books narrated by professional voice actors',
            'icon': 'fas fa-headphones',
            'features': ['Professional Narration', 'Multiple Formats', 'Speed Control', 'Bookmarking']
        },
        'research_databases': {
            'title': 'Research Databases',
            'description': 'Access academic journals, research papers, and scholarly articles',
            'icon': 'fas fa-database',
            'features': ['Academic Journals', 'Research Papers', 'Citation Tools', 'Full-Text Access']
        },
        'online_courses': {
            'title': 'Online Learning',
            'description': 'Free online courses and educational content',
            'icon': 'fas fa-graduation-cap',
            'features': ['Free Courses', 'Certificates', 'Interactive Content', 'Progress Tracking']
        }
    }
    return render(request, 'digital_resources.html', {'resources': digital_resources_data})

def community_programs(request):
    """Community Programs page with information about library programs"""
    programs_data = {
        'reading_clubs': {
            'title': 'Reading Clubs',
            'description': 'Join our book clubs and discuss literature with fellow readers',
            'icon': 'fas fa-users',
            'schedule': 'Every Saturday, 2:00 PM',
            'features': ['Monthly Book Selection', 'Group Discussions', 'Author Visits', 'Reading Challenges']
        },
        'writing_workshops': {
            'title': 'Writing Workshops',
            'description': 'Develop your writing skills with professional guidance',
            'icon': 'fas fa-pen-fancy',
            'schedule': 'Every Sunday, 10:00 AM',
            'features': ['Creative Writing', 'Poetry Sessions', 'Storytelling', 'Publishing Guidance']
        },
        'children_programs': {
            'title': 'Children\'s Programs',
            'description': 'Educational and fun activities for children of all ages',
            'icon': 'fas fa-child',
            'schedule': 'Weekdays, 4:00 PM',
            'features': ['Story Time', 'Arts & Crafts', 'Educational Games', 'Homework Help']
        },
        'technology_training': {
            'title': 'Technology Training',
            'description': 'Learn computer skills and digital literacy',
            'icon': 'fas fa-laptop',
            'schedule': 'Tuesdays & Thursdays, 6:00 PM',
            'features': ['Basic Computer Skills', 'Internet Safety', 'Digital Tools', 'Online Resources']
        }
    }
    return render(request, 'community_programs.html', {'programs': programs_data})

def custom_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return redirect('home')

class PublicSiteLoginForm(AuthenticationForm):
    pass

class PublicSiteLoginView(LoginView):
    template_name = 'account/login.html'
    authentication_form = PublicSiteLoginForm

    def form_valid(self, form):
        user = form.get_user()
        # Block superusers, staff, and users without a UserProfile
        if user.is_superuser or user.is_staff or not UserProfile.objects.filter(user=user).exists():
            form.add_error(None, 'You are not allowed to log in here. Please register as a public user.')
            return self.form_invalid(form)
        return super().form_valid(form)

def verify_otp(request):
    from public_site.models import EmailOTP
    error = None
    email = request.POST.get('email') or request.GET.get('email')
    if request.method == 'POST' and 'otp_code' in request.POST:
        otp_code = request.POST.get('otp_code')
        try:
            user = User.objects.get(email=email)
            otp_obj = EmailOTP.objects.get(user=user)
            if otp_obj.code == otp_code and not otp_obj.is_verified:
                # Session data check
                username = request.session.get('pending_username')
                password = request.session.get('pending_password')
                session_email = request.session.get('pending_email')
                if not (username and password and session_email):
                    error = 'Session expired or invalid. Please register again.'
                else:
                    user.username = username
                    user.email = session_email
                    user.set_password(password)
                    user.is_active = True
                    user.save()
                    otp_obj.is_verified = True
                    otp_obj.save()
                    # Send congratulation email
                    subject = 'Congratulations! Your Account is Verified - Public Library Bagarji'
                    from_email = 'Public Library Bagarji <kaleemullahchanna786@gmail.com>'
                    to_email = user.email
                    context = {
                        'user': user,
                        'domain': f"http://{get_current_site(request).domain}",
                        'now': timezone.now(),
                    }
                    html_content = render_to_string('account/congrat_email.html', context)
                    text_content = f"Congratulations, {user.username}!\n\nYour account has been successfully verified. Welcome to the Public Library Bagarji community!\n\nA library is not a luxury but one of the necessities of life. — Henry Ward Beecher\nJoining a community of readers is joining a community of dreamers.\nHere, you gain access to knowledge, inspiration, and lifelong friendships.\n\nWe are excited to have you with us. Explore, learn, and grow with our vibrant community. Stay tuned for updates, events, and exclusive resources!\n\n© {timezone.now().year} Public Library Bagarji. All rights reserved."
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    # Clear session data
                    request.session.pop('pending_username', None)
                    request.session.pop('pending_password', None)
                    request.session.pop('pending_email', None)
                    messages.success(request, 'Your account has been verified! You can now log in.')
                    return redirect('login')
            else:
                error = 'Invalid or expired OTP code.'
        except (User.DoesNotExist, EmailOTP.DoesNotExist):
            error = 'Invalid request.'
    # Resend OTP logic
    if request.method == 'GET' and request.GET.get('resend') == '1' and email:
        try:
            user = User.objects.get(email=email)
            otp_code = str(random.randint(100000, 999999))
            EmailOTP.objects.update_or_create(user=user, defaults={'code': otp_code, 'is_verified': False})
            subject = 'Your OTP Code - Public Library Bagarji'
            from_email = 'Public Library Bagarji <kaleemullahchanna786@gmail.com>'
            to_email = email
            context = {
                'user': user,
                'otp_code': otp_code,
                'domain': f"http://{get_current_site(request).domain}",
                'now': timezone.now(),
            }
            html_content = render_to_string('account/otp_email.html', context)
            text_content = f"Hi {user.username},\n\nYour OTP code is: {otp_code}\n\nEnter this code on the website to verify your account."
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            messages.success(request, 'A new OTP code has been sent to your email.')
        except User.DoesNotExist:
            error = 'Invalid request.'
    return render(request, 'account/verify_otp.html', {'email': email, 'error': error})
