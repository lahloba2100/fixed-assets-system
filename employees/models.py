from django.db import models
from core.models import TimeStampedModel

class Employee(TimeStampedModel):
    """
    Model for storing employee information
    """
    name = models.CharField(max_length=100, verbose_name="اسم الموظف")
    employee_id = models.CharField(max_length=50, unique=True, verbose_name="الرقم الوظيفي")
    position = models.CharField(max_length=100, verbose_name="المسمى الوظيفي")
    department = models.CharField(max_length=100, verbose_name="القسم/الإدارة")
    location = models.ForeignKey('locations.Location', on_delete=models.PROTECT, 
                               related_name='employees', verbose_name="الموقع")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="رقم الهاتف")
    email = models.EmailField(blank=True, null=True, verbose_name="البريد الإلكتروني")
    
    class Meta:
        verbose_name = "موظف"
        verbose_name_plural = "الموظفين"
        
    def __str__(self):
        return f"{self.name} ({self.employee_id})"
