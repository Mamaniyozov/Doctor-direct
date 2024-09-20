from django.contrib import admin
from .models import UserProfile, CreateUser,LoginUser
admin.site.register(CreateUser)
admin.site.register(UserProfile)
admin.site.register(LoginUser)
