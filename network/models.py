from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields import DateTimeField


class User(AbstractUser):
    following = models.ManyToManyField("User", blank=True, related_name="followers")
    likes = models.ManyToManyField("Post", blank=True, related_name="likers")
    pass


class Post(models.Model):
    content = models.CharField(max_length=200, blank=False)
    timestamp = DateTimeField(auto_now_add=True)
    writer = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")

    def __str__(self):
        return f"{self.id}. Post by {self.writer} at {self.timestamp}"

    def is_valid(self):
        return self.writer and self.content and len(self.content) <= 200