import pandas as pd
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
import uuid
from datetime import datetime

class ExcelImporter:
    """
    Class for handling Excel file imports for assets
    """
    def __init__(self):
        self.temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_imports')
        os.makedirs(self.temp_dir, exist_ok=True)
        self.field_mapping = {
            'asset_tag': 'رقم الأصل',
            'description': 'وصف الأصل',
            'group1': 'المجموعة الرئيسية',
            'group2': 'المجموعة الفرعية',
            'purchase_date': 'تاريخ الشراء',
            'purchase_cost': 'تكلفة الشراء',
            'serial_number': 'الرقم التسلسلي',
            'location': 'الموقع',
            'custodian': 'الموظف العهدة',
            'depreciation_rate': 'نسبة الإهلاك السنوية',
            'useful_life_years': 'العمر الإنتاجي',
            'salvage_value': 'القيمة التخريدية',
        }
        
    def save_uploaded_file(self, uploaded_file):
        """
        Save the uploaded Excel file to a temporary location
        """
        fs = FileSystemStorage(location=self.temp_dir)
        filename = f"{uuid.uuid4()}_{uploaded_file.name}"
        saved_file = fs.save(filename, uploaded_file)
        return os.path.join(self.temp_dir, saved_file)
    
    def read_excel_file(self, file_path):
        """
        Read Excel file and return DataFrame
        """
        try:
            df = pd.read_excel(file_path)
            return df, None
        except Exception as e:
            return None, str(e)
    
    def get_excel_columns(self, df):
        """
        Get column names from Excel file
        """
        return list(df.columns)
    
    def validate_mapping(self, column_mapping):
        """
        Validate that required fields are mapped
        """
        required_fields = ['asset_tag', 'description', 'group1', 'purchase_date', 
                          'purchase_cost', 'location', 'custodian', 'depreciation_rate']
        missing_fields = []
        
        for field in required_fields:
            if field not in column_mapping or not column_mapping[field]:
                missing_fields.append(self.field_mapping.get(field, field))
                
        return missing_fields
    
    def preview_data(self, df, column_mapping, max_rows=10):
        """
        Generate preview of data based on mapping
        """
        preview_df = df.head(max_rows).copy()
        
        # Rename columns based on mapping for preview
        preview_data = []
        for _, row in preview_df.iterrows():
            preview_row = {}
            for field, excel_column in column_mapping.items():
                if excel_column and excel_column in df.columns:
                    preview_row[self.field_mapping.get(field, field)] = row[excel_column]
                else:
                    preview_row[self.field_mapping.get(field, field)] = None
            preview_data.append(preview_row)
            
        return preview_data
    
    def validate_data(self, df, column_mapping):
        """
        Validate data in DataFrame based on mapping
        """
        errors = []
        row_num = 2  # Excel rows start at 1, and row 1 is header
        
        for _, row in df.iterrows():
            row_errors = []
            
            # Check required fields
            for field in ['asset_tag', 'description', 'group1', 'purchase_date', 
                         'purchase_cost', 'location', 'custodian', 'depreciation_rate']:
                excel_column = column_mapping.get(field)
                if excel_column and excel_column in df.columns:
                    value = row[excel_column]
                    if pd.isna(value) or value == '':
                        row_errors.append(f"الحقل '{self.field_mapping.get(field)}' مطلوب")
                
            # Validate date format
            date_column = column_mapping.get('purchase_date')
            if date_column and date_column in df.columns:
                date_value = row[date_column]
                if not pd.isna(date_value):
                    if not isinstance(date_value, (datetime, pd.Timestamp)):
                        try:
                            pd.to_datetime(date_value)
                        except:
                            row_errors.append(f"تنسيق التاريخ غير صحيح في '{self.field_mapping.get('purchase_date')}'")
            
            # Validate numeric fields
            for field in ['purchase_cost', 'depreciation_rate', 'useful_life_years', 'salvage_value']:
                excel_column = column_mapping.get(field)
                if excel_column and excel_column in df.columns:
                    value = row[excel_column]
                    if not pd.isna(value):
                        try:
                            float(value)
                        except:
                            row_errors.append(f"القيمة في '{self.field_mapping.get(field)}' يجب أن تكون رقمية")
            
            if row_errors:
                errors.append({
                    'row': row_num,
                    'errors': row_errors
                })
            
            row_num += 1
            
        return errors
    
    def process_import(self, df, column_mapping, user):
        """
        Process the actual import of data
        This is a placeholder - actual implementation would create Asset objects
        """
        # This would be implemented to create actual Asset objects
        # For each row in df, create Asset object based on column_mapping
        pass
