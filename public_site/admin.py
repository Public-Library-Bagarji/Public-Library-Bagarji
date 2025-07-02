from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import AdminUser, PublicUser, UserProfile
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Admins section: only staff or superusers
class AdminsUserAdmin(DefaultUserAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_staff=True) | qs.filter(is_superuser=True)
    def get_model_perms(self, request):
        perms = super().get_model_perms(request)
        perms['view'] = True
        return perms
    class Meta:
        verbose_name = "Admin"
        verbose_name_plural = "Admins"

# Users section: only public users (not staff, not superuser)
class PublicUserAdmin(DefaultUserAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_staff=False, is_superuser=False)
    def get_model_perms(self, request):
        perms = super().get_model_perms(request)
        perms['view'] = True
        return perms
    def phone(self, obj):
        profile = getattr(obj, 'userprofile', None)
        return profile.phone if profile else '-'
    phone.short_description = 'Phone'
    base_fields = list(DefaultUserAdmin.list_display)
    for field in ['first_name', 'last_name', 'is_staff']:
        if field in base_fields:
            base_fields.remove(field)
    list_display = tuple(base_fields) + ('phone',)
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

# Register Admins section
admin.site.register(AdminUser, AdminsUserAdmin)
# Register Users section with a different model admin name
# admin.site.register(PublicUser, PublicUserAdmin)
try:
    admin.site.unregister(PublicUser)
except Exception:
    pass

# Register the default User admin so user detail pages work, but hide from admin index
class HiddenUserAdmin(UserAdmin):
    def get_model_perms(self, request):
        # Hide from admin index
        return {}

admin.site.register(User, HiddenUserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'email', 'phone', 'gender', 'is_active', 'profile_image_tag')
    search_fields = ('user__username', 'phone')
    readonly_fields = ('profile_image',)
    list_filter = ('gender', 'user__is_active')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user__is_superuser=False, user__is_staff=False)

    def user_link(self, obj):
        if obj.user:
            url = f"/admin/auth/user/{obj.user.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'

    def email(self, obj):
        return obj.user.email if obj.user else '-'
    email.short_description = 'Email'

    def is_active(self, obj):
        return obj.user.is_active if obj.user else False
    is_active.boolean = True
    is_active.short_description = 'Active'

    def profile_image_tag(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover; border-radius:50%;" />', obj.profile_image.url)
        return "-"
    profile_image_tag.short_description = 'Profile Image'
