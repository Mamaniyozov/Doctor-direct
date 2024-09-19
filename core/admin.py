from django.contrib import admin
from .models import UserProfile, CreateUser
admin.site.register(CreateUser)
admin.site.register(UserProfile)