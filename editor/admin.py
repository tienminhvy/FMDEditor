from django.contrib import admin
from .models import *
# Register your models here.

# register post model
admin.site.register(Post)
# register comment model
admin.site.register(Comment)