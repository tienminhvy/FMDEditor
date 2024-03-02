import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

# a post model which contains title, slug (created from title), author, description, content, keyword, created date and updated date
class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    content = models.TextField()
    keyword = models.CharField(max_length=100)
    pub_date = models.DateTimeField(verbose_name="published date")
    updated_date = models.DateTimeField(verbose_name="updated date", auto_now=True)
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

# a comment model which contains content, created date and updated date. A comment belongs to a post, published by a user
class Comment(models.Model):
    content = models.TextField()
    created_date = models.DateTimeField(verbose_name="created date", auto_now_add=True)
    updated_date = models.DateTimeField(verbose_name="updated date", auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)