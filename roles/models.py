from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_author = models.BooleanField()
    is_reviewer = models.BooleanField()
    is_teacher = models.BooleanField()
    needs_teacher_review = models.BooleanField(default=True)

    def __str__(self):
        return "Profile for " + self.user.username
