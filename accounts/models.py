from django.db import models
from django.contrib.auth.models import AbstractUser
from employees.models import Employee

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    # Add related_name to fix the clash with auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    employee = models.OneToOneField(Employee, on_delete=models.SET_NULL, 
                                   null=True, blank=True, 
                                   related_name='user_account',
                                   verbose_name="الموظف المرتبط")
    
    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمين"
        
    def __str__(self):
        return self.username

class Role(models.Model):
    """
    Model for storing user roles and permissions
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم الدور")
    description = models.TextField(blank=True, null=True, verbose_name="وصف الدور")
    
    class Meta:
        verbose_name = "دور"
        verbose_name_plural = "الأدوار"
        
    def __str__(self):
        return self.name
