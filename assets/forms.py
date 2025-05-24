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
