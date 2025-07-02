# Public Library Bagarji

A modern, responsive Django-based public library management system with a beautiful fire-themed UI.

## 🌟 Features

### 📚 Book Management
- Complete book catalog with search functionality
- Book categories and filtering
- PDF book downloads
- Book reviews and ratings
- Book detail pages with comments

### 📰 Content Management
- Blog articles with markdown support
- News section with latest updates
- Book reviews section
- Rich text editor for content creation

### 🔍 Advanced Search
- Real-time search suggestions
- Category-based filtering
- Multiple sorting options (newest, oldest, alphabetical)
- Responsive search interface

### 👥 User Management
- User registration with email verification
- User profiles with profile pictures
- Login/logout functionality
- Comment system for books and articles

### 🎨 Beautiful UI/UX
- Fire-themed design with orange gradients
- Fully responsive design (mobile-friendly)
- Smooth animations and transitions
- Dark mode support
- Modern pagination system

### 📱 Mobile Responsive
- Optimized for all screen sizes
- Touch-friendly interface
- Mobile-optimized navigation
- Responsive search and filtering

## 🚀 Technology Stack

- **Backend**: Django 5.2.3
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Styling**: Custom CSS with fire theme
- **Icons**: Font Awesome
- **Admin**: Django Jazzmin

## 📋 Requirements

- Python 3.8+
- Django 5.2.3
- Pillow (for image processing)
- Django CORS Headers
- Django Simple History
- Django Jazzmin

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd public_library_bagarji
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env file with your configuration
   # Important: Change the SECRET_KEY and EMAIL_HOST_PASSWORD
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## 📁 Project Structure

```
public_library_bagarji/
├── library_admin/          # Main Django app
│   ├── models.py          # Database models
│   ├── views.py           # API views
│   ├── admin.py           # Admin configuration
│   └── urls.py            # URL routing
├── public_site/           # Public site app
│   ├── views.py           # Public views
│   ├── models.py          # User models
│   └── urls.py            # Public URLs
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── books.html         # Books page
│   ├── blogs.html         # Blogs page
│   └── ...                # Other templates
├── static/                # Static files
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Images
├── media/                 # User uploaded files
└── manage.py              # Django management script
```

## 🎯 Key Features Explained

### Search System
- **Real-time suggestions**: As you type, book suggestions appear
- **Keyboard navigation**: Use arrow keys to navigate suggestions
- **Category filtering**: Filter books by category
- **Multiple sorting**: Sort by newest, oldest, or alphabetical order

### Responsive Design
- **Mobile-first approach**: Optimized for mobile devices
- **Flexible grid system**: Adapts to different screen sizes
- **Touch-friendly**: Large buttons and touch targets
- **Fast loading**: Optimized images and assets

### Admin Panel
- **Beautiful interface**: Django Jazzmin admin theme
- **Content management**: Easy to add/edit books, blogs, news
- **User management**: Manage users and permissions
- **Comment moderation**: Moderate user comments

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory by copying `env.example`:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.100.22

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Public Library Bagarji <your-email@gmail.com>

# Database (for production, use PostgreSQL)
DATABASE_URL=sqlite:///db.sqlite3
```

### Security Setup
1. **Generate a new SECRET_KEY**:
   ```python
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

2. **Set up Gmail App Password**:
   - Go to Google Account settings
   - Enable 2-factor authentication
   - Generate an App Password for your application
   - Use this password in EMAIL_HOST_PASSWORD

3. **Production Settings**:
   - Set `DEBUG=False`
   - Use a strong SECRET_KEY
   - Configure a production database (PostgreSQL recommended)
   - Set up HTTPS
   - Configure proper ALLOWED_HOSTS

## 🚀 Deployment

### Production Setup
1. Set `DEBUG = False` in settings
2. Configure a production database (PostgreSQL recommended)
3. Set up static file serving
4. Configure email settings
5. Set up HTTPS

### Docker Deployment
```bash
# Build the image
docker build -t public-library-bagarji .

# Run the container
docker run -p 8000:8000 public-library-bagarji
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Kaleemullah Channa**
- Email: kaleemullahchanna786@gmail.com
- GitHub: [Your GitHub Profile]

## 🙏 Acknowledgments

- Django community for the excellent framework
- Font Awesome for beautiful icons
- Django Jazzmin for the beautiful admin interface
- All contributors and users of this project

---

**Made with ❤️ for Public Library Bagarji** 