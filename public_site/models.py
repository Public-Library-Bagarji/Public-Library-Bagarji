from django.contrib.auth.models import User
from django.db import models
import os
from django.conf import settings
from django.contrib.sessions.models import Session
from django.db.models.signals import post_delete
from django.dispatch import receiver

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    profile_image = models.ImageField(upload_to='uploads/profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.username

    def delete(self, *args, **kwargs):
        # Delete profile image file from storage
        if self.profile_image and self.profile_image.name:
            image_path = self.profile_image.path
            if os.path.isfile(image_path):
                try:
                    os.remove(image_path)
                except Exception:
                    pass
        super().delete(*args, **kwargs)

class EmailOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_otp')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.user.username}"

@receiver(post_delete, sender=User)
def delete_user_sessions(sender, instance, **kwargs):
    sessions = Session.objects.all()
    for session in sessions:
        data = session.get_decoded()
        if data.get('_auth_user_id') == str(instance.id):
            session.delete()

class AdminUser(User):
    class Meta:
        proxy = True
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'

class PublicUser(User):
    class Meta:
        proxy = True
        verbose_name = 'User'
        verbose_name_plural = 'Users'
