from django.contrib.auth.models import User
from django.db import models
from companies.models import Company
from users.utils import user_photo_path


class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name='customuser')
    photo = models.ImageField(upload_to=user_photo_path, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)

class UserCompany(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'company')
