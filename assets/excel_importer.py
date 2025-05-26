import pandas as pd
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.utils.dateparse import parse_date
import os
import uuid
from datetime import datetime

# Import models needed for lookup and creation
from .models import Asset, AssetCategory, AssetSubcategory
from locations.models import Branch
from employees.models import Employee

class ExcelImporter:
    """
    Class for handling Excel file imports for assets
    """
    def __init__(self):
        self.temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_imports')
        os.makedirs(self.temp_dir, exist_ok=True)
        # Mapping internal field names to user-friendly Arabic names (for display/validation messages)
        # And also defining which Excel column maps to which internal field (done in view)
        self.field_mapping = {
            # Internal Field Name : User-Facing Arabic Name
            'code': 'كود الأصل', # Changed from asset_tag for consistency with model
            'name': 'اسم الأصل', # Added, assuming description might be too long for a name
            'description': 'وصف الأصل',
            'category_name': 'المجموعة الرئيسية', # Expecting name in Excel
            'subcategory_name': 'المجموعة الفرعية', # Expecting name in Excel
            'acquisition_date': 'تاريخ الاقتناء', # Changed from purchase_date
            'acquisition_cost': 'تكلفة الاقتناء', # Changed from purchase_cost
            # 'serial_number': 'الرقم التسلسلي', # Not currently in Asset model, maybe add later?
            'location_name': 'الفرع', # Expecting name in Excel, changed from 'location'
            'custodian_name': 'الموظف المسؤول', # Expecting name/ID in Excel, changed from 'custodian'
            # 'depreciation_rate': 'نسبة الإهلاك السنوية', # Rate is derived from Category, not stored directly on Asset
            'useful_life_years': 'العمر الإنتاجي (سنوات)',
            'salvage_value': 'القيمة التخريدية',
            'depreciation_start_date': 'تاريخ بدء الإهلاك', # Added
        }
        # Define which fields are absolutely required from the Excel file
        self.required_excel_fields = [
            'code', 'name', 'category_name', 'subcategory_name', 
            'acquisition_date', 'acquisition_cost', 'useful_life_years', 
            'location_name', 'custodian_name', 'depreciation_start_date'
        ]

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
            # Convert all columns to string initially to avoid type issues with pandas guessing
            df = pd.read_excel(file_path, dtype=str)
            # Replace NaN/NaT values with empty strings for easier handling
            df = df.fillna('')
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
        Validate that required fields (as defined in self.required_excel_fields) are mapped
        """
        missing_fields = []
        for field in self.required_excel_fields:
            if field not in column_mapping or not column_mapping[field]:
                missing_fields.append(self.field_mapping.get(field, field))
        return missing_fields

    def preview_data(self, df, column_mapping, max_rows=10):
        """
        Generate preview of data based on mapping
        """
        preview_df = df.head(max_rows).copy()
        preview_data = []
        headers = [self.field_mapping.get(f, f) for f in column_mapping.keys() if column_mapping[f]]
        
        for _, row in preview_df.iterrows():
            preview_row = {}
            for field, excel_column in column_mapping.items():
                if excel_column and excel_column in df.columns:
                    # Get the user-facing name for the preview header
                    header_name = self.field_mapping.get(field, field)
                    preview_row[header_name] = row[excel_column]
                # else: # Don't include unmapped fields in preview
                #     header_name = self.field_mapping.get(field, field)
                #     preview_row[header_name] = None 
            preview_data.append(preview_row)
            
        # Ensure consistent order based on mapping keys
        ordered_preview_data = []
        ordered_headers = [self.field_mapping.get(f, f) for f in column_mapping.keys() if column_mapping[f]]
        for row in preview_data:
             ordered_row = {h: row.get(h, '') for h in ordered_headers}
             ordered_preview_data.append(ordered_row)

        return ordered_headers, ordered_preview_data

    def validate_data(self, df, column_mapping):
        """
        Validate data in DataFrame based on mapping and model constraints
        """
        errors = []
        row_num = 2  # Excel rows start at 1, header is row 1

        # Pre-fetch existing codes to check for duplicates within the file and DB
        existing_db_codes = set(Asset.objects.values_list('code', flat=True))
        codes_in_file = set()

        for index, row in df.iterrows():
            row_errors = []
            
            # --- Field Existence and Basic Format Validation --- 
            asset_data = {}
            for field, excel_column in column_mapping.items():
                if excel_column and excel_column in df.columns:
                    value = str(row[excel_column]).strip() # Ensure string and strip whitespace
                    asset_data[field] = value
                    # Check if required fields are empty
                    if field in self.required_excel_fields and not value:
                         row_errors.append(f"الحقل الإلزامي '{self.field_mapping.get(field)}' فارغ.")
                elif field in self.required_excel_fields:
                    # This case should be caught by validate_mapping, but double-check
                    row_errors.append(f"لم يتم ربط عمود للحقل الإلزامي '{self.field_mapping.get(field)}'.")

            # --- Specific Field Validations --- 
            
            # Code: Check uniqueness (DB and within file)
            code = asset_data.get('code')
            if code:
                if code in existing_db_codes:
                    row_errors.append(f"كود الأصل '{code}' موجود بالفعل في قاعدة البيانات.")
                if code in codes_in_file:
                     row_errors.append(f"كود الأصل '{code}' مكرر في الملف.")
                else:
                    codes_in_file.add(code)
            
            # Dates: Check format (YYYY-MM-DD)
            for field in ['acquisition_date', 'depreciation_start_date']:
                date_str = asset_data.get(field)
                if date_str:
                    parsed_date = parse_date(date_str)
                    if parsed_date is None:
                        row_errors.append(f"تنسيق التاريخ غير صحيح للحقل '{self.field_mapping.get(field)}'. استخدم YYYY-MM-DD.")
                    else:
                         asset_data[field] = parsed_date # Store parsed date for later use
            
            # Numeric Fields: Check if convertible to number
            for field in ['acquisition_cost', 'useful_life_years', 'salvage_value']:
                num_str = asset_data.get(field)
                if num_str:
                    try:
                        # Use float for cost/value, int for years
                        if field == 'useful_life_years':
                            num_val = int(num_str)
                            if num_val <= 0:
                                 row_errors.append(f"قيمة '{self.field_mapping.get(field)}' يجب أن تكون أكبر من صفر.")
                        else:
                             num_val = float(num_str)
                             if num_val < 0:
                                 row_errors.append(f"قيمة '{self.field_mapping.get(field)}' لا يمكن أن تكون سالبة.")
                        asset_data[field] = num_val # Store converted number
                    except (ValueError, TypeError):
                        row_errors.append(f"القيمة في '{self.field_mapping.get(field)}' يجب أن تكون رقمية.")
                elif field in ['acquisition_cost', 'useful_life_years']: # These numerics are required
                     if field not in [err.split("'")[1] for err in row_errors if 'فارغ' in err]: # Avoid duplicate error msg
                          row_errors.append(f"الحقل الرقمي الإلزامي '{self.field_mapping.get(field)}' فارغ.")

            # --- Foreign Key Lookups --- 
            # Category & Subcategory
            category_name = asset_data.get('category_name')
            subcategory_name = asset_data.get('subcategory_name')
            category = None
            if category_name:
                try:
                    category = AssetCategory.objects.get(name=category_name)
                    asset_data['category_obj'] = category # Store object for later
                    if subcategory_name:
                        try:
                            subcategory = AssetSubcategory.objects.get(category=category, name=subcategory_name)
                            asset_data['subcategory_obj'] = subcategory # Store object
                        except AssetSubcategory.DoesNotExist:
                            row_errors.append(f"المجموعة الفرعية '{subcategory_name}' غير موجودة ضمن المجموعة الرئيسية '{category_name}'.")
                    elif 'subcategory_name' in self.required_excel_fields: # Check if subcat is required
                         row_errors.append(f"الحقل الإلزامي '{self.field_mapping.get('subcategory_name')}' فارغ.")
                except AssetCategory.DoesNotExist:
                    row_errors.append(f"المجموعة الرئيسية '{category_name}' غير موجودة.")
            
            # Location (Branch)
            location_name = asset_data.get('location_name')
            if location_name:
                try:
                    location = Branch.objects.get(name=location_name)
                    asset_data['location_obj'] = location # Store object
                except Branch.DoesNotExist:
                    row_errors.append(f"الفرع '{location_name}' غير موجود.")
            
            # Custodian (Employee) - Assuming lookup by name for simplicity
            custodian_name = asset_data.get('custodian_name')
            if custodian_name:
                try:
                    # This might be ambiguous if names are not unique. Consider using Employee ID.
                    custodian = Employee.objects.get(name=custodian_name) 
                    asset_data['custodian_obj'] = custodian # Store object
                except Employee.DoesNotExist:
                    row_errors.append(f"الموظف '{custodian_name}' غير موجود.")
                except Employee.MultipleObjectsReturned:
                     row_errors.append(f"يوجد أكثر من موظف باسم '{custodian_name}'. يرجى استخدام معرف فريد.")

            if row_errors:
                errors.append({
                    'row': row_num,
                    'errors': row_errors
                })
            
            row_num += 1
            
        return errors

    @transaction.atomic
    def process_import(self, df, column_mapping, user):
        """
        Process the actual import of data after validation.
        Assumes data has been validated by validate_data.
        """
        success_count = 0
        failure_count = 0
        failures = [] # List of dictionaries: {'row': row_num, 'errors': [error_msg]} 
        row_num = 2 # Excel row number

        for index, row in df.iterrows():
            asset_data = {}
            import_errors = []
            try:
                # 1. Extract data using mapping
                for field, excel_column in column_mapping.items():
                    if excel_column and excel_column in df.columns:
                        asset_data[field] = str(row[excel_column]).strip()
                    else:
                        asset_data[field] = None # Handle unmapped optional fields
                
                # 2. Data Type Conversion (redundant if validate_data stores converted values, but safer)
                try:
                    acquisition_cost = float(asset_data['acquisition_cost']) if asset_data.get('acquisition_cost') else 0.0
                    useful_life_years = int(asset_data['useful_life_years']) if asset_data.get('useful_life_years') else 0
                    salvage_value = float(asset_data.get('salvage_value', 0.0)) if asset_data.get('salvage_value') else 0.0
                    acquisition_date = parse_date(asset_data['acquisition_date']) if asset_data.get('acquisition_date') else None
                    depreciation_start_date = parse_date(asset_data['depreciation_start_date']) if asset_data.get('depreciation_start_date') else None
                except (ValueError, TypeError) as e:
                    import_errors.append(f"خطأ في تحويل البيانات الرقمية/التاريخ: {e}")
                    raise ValueError("Data conversion error") # Skip to failure handling

                # 3. Foreign Key Lookups (can reuse logic from validation or re-fetch)
                try:
                    category = AssetCategory.objects.get(name=asset_data['category_name'])
                    subcategory = AssetSubcategory.objects.get(category=category, name=asset_data['subcategory_name'])
                    location = Branch.objects.get(name=asset_data['location_name'])
                    custodian = Employee.objects.get(name=asset_data['custodian_name']) # Assuming name is unique enough for import
                except (AssetCategory.DoesNotExist, AssetSubcategory.DoesNotExist, Branch.DoesNotExist, Employee.DoesNotExist, Employee.MultipleObjectsReturned) as e:
                    import_errors.append(f"خطأ في البحث عن بيانات مرتبطة: {e}")
                    raise ValueError("Foreign key lookup error") # Skip to failure handling
                
                # 4. Check for existing asset code again (within transaction)
                if Asset.objects.filter(code=asset_data['code']).exists():
                     import_errors.append(f"كود الأصل '{asset_data['code']}' موجود بالفعل.")
                     raise ValueError("Duplicate asset code")

                # 5. Create Asset instance
                new_asset = Asset(
                    code=asset_data['code'],
                    name=asset_data.get('name', ''), # Use provided name
                    description=asset_data.get('description', ''),
                    subcategory=subcategory,
                    acquisition_date=acquisition_date,
                    acquisition_cost=acquisition_cost,
                    salvage_value=salvage_value,
                    useful_life_years=useful_life_years,
                    location=location,
                    custodian=custodian,
                    depreciation_start_date=depreciation_start_date,
                    created_by=user,
                    status='active' # Default status
                )
                
                # 6. Validate and Save
                new_asset.full_clean() # Run model validation
                new_asset.save()
                success_count += 1
                
            except Exception as e:
                # Catch any error during processing of this row
                failure_count += 1
                # If specific errors weren't added, add the general exception message
                if not import_errors:
                    import_errors.append(f"خطأ عام: {e}")
                failures.append({'row': row_num, 'code': asset_data.get('code', 'N/A'), 'errors': import_errors})
                # Continue to the next row
            
            row_num += 1
            
        # If any failures occurred, the transaction will be rolled back by the @transaction.atomic decorator
        # We need to raise an exception to trigger the rollback if failures happened.
        if failure_count > 0:
             # This message won't be shown directly to user, but signals transaction failure
             raise Exception(f"Import failed for {failure_count} rows. Rolling back transaction.")

        return success_count, failure_count, failures # This line is only reached if failure_count is 0

    def cleanup_temp_file(self, file_path):
        """
        Delete the temporary file.
        """
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except OSError as e:
            # Log this error, but don't prevent the user flow
            print(f"Error deleting temp file {file_path}: {e}")
            pass

