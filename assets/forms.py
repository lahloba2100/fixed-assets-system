from django import forms
from django.core.validators import FileExtensionValidator

class ExcelUploadForm(forms.Form):
    """
    Form for uploading Excel files for asset import
    """
    excel_file = forms.FileField(
        label="ملف Excel",
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        help_text="يرجى تحميل ملف Excel بصيغة .xlsx أو .xls"
    )



from .models import Asset, AssetCategory, AssetSubcategory
from locations.models import Branch
from employees.models import Employee

class AssetForm(forms.ModelForm):
    """
    Form for creating and updating Asset objects
    """
    category = forms.ModelChoiceField(
        queryset=AssetCategory.objects.all(),
        label="المجموعة الرئيسية",
        empty_label="اختر المجموعة الرئيسية",
        widget=forms.Select(attrs={'class': 'form-control', 'hx-get': '/assets/load-subcategories/', 'hx-target': '#id_subcategory'})
    )
    subcategory = forms.ModelChoiceField(
        queryset=AssetSubcategory.objects.none(),  # Initially empty
        label="المجموعة الفرعية",
        empty_label="اختر المجموعة الفرعية أولاً",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    location = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        label="الفرع",
        empty_label="اختر الفرع",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    custodian = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        label="الموظف المسؤول",
        empty_label="اختر الموظف",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Asset
        fields = [
            'code', 'name', 'description', 'category', 'subcategory', 
            'acquisition_date', 'acquisition_cost', 'salvage_value', 
            'useful_life_years', 'location', 'custodian', 
            'depreciation_start_date'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'acquisition_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'acquisition_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'salvage_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'useful_life_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'depreciation_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'code': "كود الأصل",
            'name': "اسم الأصل",
            'description': "وصف الأصل",
            'acquisition_date': "تاريخ الاقتناء",
            'acquisition_cost': "تكلفة الاقتناء",
            'salvage_value': "القيمة التخريدية",
            'useful_life_years': "العمر الإنتاجي (سنوات)",
            'depreciation_start_date': "تاريخ بدء الإهلاك",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = AssetSubcategory.objects.filter(category_id=category_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from browser; ignore and fallback to empty queryset
        elif self.instance.pk and self.instance.subcategory:
            self.fields['category'].initial = self.instance.subcategory.category
            self.fields['subcategory'].queryset = self.instance.subcategory.category.subcategories.order_by('name')
            self.fields['subcategory'].initial = self.instance.subcategory




from .models import AssetTransfer, AssetDisposal

class AssetTransferForm(forms.ModelForm):
    """
    Form for creating AssetTransfer objects
    """
    asset = forms.ModelChoiceField(
        queryset=Asset.objects.filter(status='active'), # Only allow transfer of active assets
        label="الأصل المراد نقله",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    to_location = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        label="الفرع الجديد",
        empty_label="اختر الفرع الجديد",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    to_custodian = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        label="الموظف المسؤول الجديد",
        empty_label="اختر الموظف الجديد",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = AssetTransfer
        fields = ['asset', 'transfer_date', 'to_location', 'to_custodian', 'notes']
        widgets = {
            'transfer_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'transfer_date': "تاريخ النقل",
            'notes': "ملاحظات",
        }

    def clean(self):
        cleaned_data = super().clean()
        asset = cleaned_data.get("asset")
        to_location = cleaned_data.get("to_location")
        to_custodian = cleaned_data.get("to_custodian")

        if asset and to_location and asset.location == to_location:
            self.add_error('to_location', "الفرع الجديد يجب أن يكون مختلفاً عن الفرع الحالي.")
            
        # Optionally add validation for custodian change if needed
        # if asset and to_custodian and asset.custodian == to_custodian:
        #     self.add_error('to_custodian', "الموظف الجديد يجب أن يكون مختلفاً عن الموظف الحالي.")

        return cleaned_data

class AssetDisposalForm(forms.ModelForm):
    """
    Form for creating AssetDisposal objects
    """
    asset = forms.ModelChoiceField(
        queryset=Asset.objects.filter(status='active'), # Only allow disposal of active assets
        label="الأصل المراد استبعاده",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = AssetDisposal
        fields = ['asset', 'disposal_date', 'disposal_type', 'sale_amount', 'notes']
        widgets = {
            'disposal_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'disposal_type': forms.Select(attrs={'class': 'form-control'}),
            'sale_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'disposal_date': "تاريخ الاستبعاد",
            'disposal_type': "نوع الاستبعاد",
            'sale_amount': "مبلغ البيع (إن وجد)",
            'notes': "ملاحظات",
        }

    def clean(self):
        cleaned_data = super().clean()
        disposal_type = cleaned_data.get("disposal_type")
        sale_amount = cleaned_data.get("sale_amount")

        if disposal_type == 'sale' and (sale_amount is None or sale_amount < 0):
            self.add_error('sale_amount', "مبلغ البيع مطلوب ولا يمكن أن يكون سالباً في حالة البيع.")
        elif disposal_type == 'write_off' and sale_amount is not None and sale_amount != 0:
             # Optionally clear sale_amount if it's a write-off, or raise an error
             # cleaned_data['sale_amount'] = None 
             self.add_error('sale_amount', "لا يجب تحديد مبلغ بيع في حالة التكهين.")
             
        return cleaned_data

