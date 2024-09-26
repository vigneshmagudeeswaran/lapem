from django.db import models
from django.contrib.auth.models import Permission

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
# Create your models here.
from django.contrib.auth.models import PermissionsMixin


class MyUserManager(BaseUserManager):
    def create_user(self, email, name, **extra_fields):
        
        if not email:
            raise ValueError('Users must have an email address')
        if not name:
            raise ValueError('Users must have a name')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            date_of_birth=date_of_birth,
        )

        user.save(using=self._db)
        return user

    def create_superuser(self, email, date_of_birth, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            date_of_birth=date_of_birth,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class Organization(AbstractBaseUser,PermissionsMixin):
    name = models.CharField(max_length=100)
    tin_id = models.AutoField(primary_key=True)
    email = models.EmailField(null=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_subscribed = models.BooleanField(default=False)
    subscription_start=models.DateTimeField(null=True)
    subscription_extended=models.BooleanField(default=False)
    subscription_end=models.DateTimeField(auto_now_add=True)
    auth0_user_id = models.CharField(max_length=100, unique=True, null=True)
    

    
    objects = MyUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f'organization name is {self.name}'

# class Role(models.Model):
#     name = models.CharField(max_length=255)
#     permissions = models.ManyToManyField(Permission)
    
#     def __str__(self):
#         return f'role name is {self.name} and permissions are {self.permissions}'
 
# class OrgAdmin(AbstractBaseUser):
#     username = models.CharField(max_length=100, unique=True)
#     Organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
#     email = models.EmailField(null=False, unique=True)
#     permissions = models.ManyToManyField(Role)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     objects = MyUserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']

#     def __str__(self):
#         return f'admin name is {self.username} and username is {self.username}'