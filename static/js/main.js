/* Custom JavaScript for Public Library Bagarji */

document.addEventListener('DOMContentLoaded', () => {
    // Theme Management
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = themeToggle.querySelector('i');
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    // Theme toggle click handler
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        // Update theme
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Update icon with animation
        themeIcon.style.transform = 'rotate(360deg)';
        setTimeout(() => {
            updateThemeIcon(newTheme);
            themeIcon.style.transform = '';
        }, 300);
    });
    
    // Update theme icon
    function updateThemeIcon(theme) {
        themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Lazy loading for images
    const lazyImages = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });

    lazyImages.forEach(image => {
        imageObserver.observe(image);
    });

    // Scroll Animations
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.fade-in-up, .fade-in-left, .fade-in-right, .scale-in, .hero-subtitle, .section-title, .card');
        
        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementBottom = element.getBoundingClientRect().bottom;
            const windowHeight = window.innerHeight;
            
            // Add visible class when element is in viewport
            if (elementTop < windowHeight * 0.85 && elementBottom > 0) {
                element.classList.add('visible');
            }
        });
    };

    // Initial check for elements in viewport
    animateOnScroll();

    // Add scroll event listener
    window.addEventListener('scroll', () => {
        requestAnimationFrame(animateOnScroll);
    });

    // Add animation classes to elements
    document.querySelectorAll('.hero-subtitle').forEach(el => el.classList.add('fade-in-up'));
    document.querySelectorAll('.section-title').forEach(el => el.classList.add('fade-in-up'));
    document.querySelectorAll('.card').forEach((el, index) => {
        el.classList.add('fade-in-up');
        el.style.transitionDelay = `${index * 0.1}s`; // Stagger the animations
    });

    // --- Navbar mobile menu close on outside click ---
    document.addEventListener('click', function(event) {
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.getElementById('navbarNav');
        if (!navbarToggler || !navbarCollapse) return;
        const isOpen = navbarCollapse.classList.contains('show');
        // If menu is open and click is outside both toggler and menu
        if (isOpen && !navbarCollapse.contains(event.target) && !navbarToggler.contains(event.target)) {
            navbarToggler.click(); // This will close the menu
        }
    });
}); 