from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import AdminUser, PublicUser

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
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

# Register Admins section
admin.site.register(AdminUser, AdminsUserAdmin)
# Register Users section with a different model admin name
admin.site.register(PublicUser, PublicUserAdmin)
