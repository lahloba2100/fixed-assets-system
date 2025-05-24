from django.db import models
from core.models import TimeStampedModel

class Location(TimeStampedModel):
    """
    Model for storing location information (branches and governorates)
    """
    LOCATION_TYPES = (
        ('branch', 'فرع'),
        ('governorate', 'محافظة'),
    )
    
    name = models.CharField(max_length=100, verbose_name="اسم الموقع")
    type = models.CharField(max_length=20, choices=LOCATION_TYPES, verbose_name="نوع الموقع")
    parent_location = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                       related_name='child_locations', verbose_name="الموقع الأب")
    address = models.TextField(blank=True, null=True, verbose_name="العنوان")
    
    class Meta:
        verbose_name = "موقع"
        verbose_name_plural = "المواقع"
        
    def __str__(self):
        return self.name

class Branch(Location):
    """
    Proxy model for Branch locations
    """
    class Meta:
        proxy = True
        verbose_name = "فرع"
        verbose_name_plural = "الفروع"
    
    def save(self, *args, **kwargs):
        self.type = 'branch'
        super().save(*args, **kwargs)
        
    @classmethod
    def get_branches(cls):
        return cls.objects.filter(type='branch')
