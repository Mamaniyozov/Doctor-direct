from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    email = models.EmailField()
    password = models.CharField(max_length=10)
    push_token = models.CharField(max_length=255, blank=True, null=True) 

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
    

class CreateUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=50)                                     
    lastname = models.CharField(max_length=50)
    email = models.EmailField(default='default@example.com')
    password = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.firstname} {self.lastname} {self.email} {self.password}"
    
# Create your models here.
