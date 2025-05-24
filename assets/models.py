from django.conf import settings
from django.db import models

class AssetCategory(models.Model):
    """
    Model for primary asset categories (مجموعة 1)
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم المجموعة")
    description = models.TextField(blank=True, null=True, verbose_name="وصف المجموعة")
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="نسبة الإهلاك")
    
    class Meta:
        verbose_name = "مجموعة أصول رئيسية"
        verbose_name_plural = "مجموعات الأصول الرئيسية"
        
    def __str__(self):
        return self.name

class AssetSubcategory(models.Model):
    """
    Model for secondary asset subcategories (مجموعة 2)
    """
    category = models.ForeignKey(AssetCategory, on_delete=models.CASCADE, 
                                related_name='subcategories', 
                                verbose_name="المجموعة الرئيسية")
    name = models.CharField(max_length=100, verbose_name="اسم المجموعة الفرعية")
    description = models.TextField(blank=True, null=True, verbose_name="وصف المجموعة الفرعية")
    
    class Meta:
        verbose_name = "مجموعة أصول فرعية"
        verbose_name_plural = "مجموعات الأصول الفرعية"
        unique_together = ('category', 'name')
        
    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Asset(models.Model):
    """
    Model for fixed assets
    """
    STATUS_CHOICES = (
        ('active', 'نشط'),
        ('transferred', 'منقول'),
        ('disposed', 'مستبعد'),
    )
    
    # Basic information
    code = models.CharField(max_length=50, unique=True, verbose_name="كود الأصل")
    name = models.CharField(max_length=200, verbose_name="اسم الأصل")
    description = models.TextField(blank=True, null=True, verbose_name="وصف الأصل")
    subcategory = models.ForeignKey(AssetSubcategory, on_delete=models.PROTECT, 
                                   related_name='assets', 
                                   verbose_name="المجموعة الفرعية")
    
    # Financial information
    acquisition_date = models.DateField(verbose_name="تاريخ الاقتناء")
    acquisition_cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="تكلفة الاقتناء")
    salvage_value = models.DecimalField(max_digits=12, decimal_places=2, default=0, 
                                       verbose_name="القيمة التخريدية")
    useful_life_years = models.PositiveIntegerField(verbose_name="العمر الإنتاجي (سنوات)")
    
    # Location and custody
    location = models.ForeignKey('locations.Branch', on_delete=models.PROTECT, 
                               related_name='assets', 
                               verbose_name="الفرع")
    custodian = models.ForeignKey('employees.Employee', on_delete=models.PROTECT, 
                                 related_name='assets_in_custody', 
                                 verbose_name="الموظف المسؤول")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', 
                             verbose_name="حالة الأصل")
    
    # Depreciation tracking
    depreciation_start_date = models.DateField(verbose_name="تاريخ بدء الإهلاك")
    accumulated_depreciation = models.DecimalField(max_digits=12, decimal_places=2, default=0, 
                                                 verbose_name="مجمع الإهلاك")
    last_depreciation_date = models.DateField(null=True, blank=True, 
                                            verbose_name="تاريخ آخر إهلاك")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                  null=True, related_name='created_assets', 
                                  verbose_name="تم الإنشاء بواسطة")
    
    class Meta:
        verbose_name = "أصل ثابت"
        verbose_name_plural = "الأصول الثابتة"
        
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def net_book_value(self):
        """Calculate current net book value"""
        return self.acquisition_cost - self.accumulated_depreciation
    
    @property
    def depreciation_rate(self):
        """Get depreciation rate from category"""
        return self.subcategory.category.depreciation_rate

class AssetTransfer(models.Model):
    """
    Model for tracking asset transfers between branches or employees
    """
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, 
                             related_name='transfers', 
                             verbose_name="الأصل")
    transfer_date = models.DateField(verbose_name="تاريخ النقل")
    
    # From
    from_location = models.ForeignKey('locations.Branch', on_delete=models.PROTECT, 
                                     related_name='outgoing_transfers', 
                                     verbose_name="من الفرع")
    from_custodian = models.ForeignKey('employees.Employee', on_delete=models.PROTECT, 
                                      related_name='outgoing_transfers', 
                                      verbose_name="من الموظف")
    
    # To
    to_location = models.ForeignKey('locations.Branch', on_delete=models.PROTECT, 
                                   related_name='incoming_transfers', 
                                   verbose_name="إلى الفرع")
    to_custodian = models.ForeignKey('employees.Employee', on_delete=models.PROTECT, 
                                    related_name='incoming_transfers', 
                                    verbose_name="إلى الموظف")
    
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                  null=True, related_name='created_transfers', 
                                  verbose_name="تم الإنشاء بواسطة")
    
    class Meta:
        verbose_name = "نقل أصل"
        verbose_name_plural = "نقل الأصول"
        
    def __str__(self):
        return f"نقل {self.asset.code} بتاريخ {self.transfer_date}"

class AssetDisposal(models.Model):
    """
    Model for tracking asset disposals (تكهين/بيع)
    """
    DISPOSAL_TYPE_CHOICES = (
        ('write_off', 'تكهين'),
        ('sale', 'بيع'),
    )
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, 
                             related_name='disposals', 
                             verbose_name="الأصل")
    disposal_date = models.DateField(verbose_name="تاريخ الاستبعاد")
    disposal_type = models.CharField(max_length=20, choices=DISPOSAL_TYPE_CHOICES, 
                                    verbose_name="نوع الاستبعاد")
    
    # Financial information
    book_value_at_disposal = models.DecimalField(max_digits=12, decimal_places=2, 
                                               verbose_name="القيمة الدفترية عند الاستبعاد")
    sale_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, 
                                     verbose_name="مبلغ البيع")
    
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                  null=True, related_name='created_disposals', 
                                  verbose_name="تم الإنشاء بواسطة")
    
    class Meta:
        verbose_name = "استبعاد أصل"
        verbose_name_plural = "استبعاد الأصول"
        
    def __str__(self):
        return f"استبعاد {self.asset.code} بتاريخ {self.disposal_date}"

class DepreciationEntry(models.Model):
    """
    Model for tracking monthly depreciation entries
    """
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, 
                             related_name='depreciation_entries', 
                             verbose_name="الأصل")
    period_date = models.DateField(verbose_name="تاريخ الفترة")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="مبلغ الإهلاك")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                  null=True, related_name='created_depreciation_entries', 
                                  verbose_name="تم الإنشاء بواسطة")
    
    class Meta:
        verbose_name = "قيد إهلاك"
        verbose_name_plural = "قيود الإهلاك"
        unique_together = ('asset', 'period_date')
        
    def __str__(self):
        return f"إهلاك {self.asset.code} لشهر {self.period_date}"
