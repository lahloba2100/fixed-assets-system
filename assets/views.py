from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Asset, AssetCategory, AssetSubcategory, AssetTransfer, AssetDisposal, DepreciationEntry
from .forms import AssetForm, ExcelUploadForm, AssetTransferForm, AssetDisposalForm
from .excel_importer import ExcelImporter
import os

@login_required
def asset_list(request):
    """Display a list of all assets."""
    assets = Asset.objects.select_related('subcategory__category', 'location', 'custodian').all()
    context = {
        'title': 'قائمة الأصول',
        'assets': assets
    }
    return render(request, 'assets/asset_list.html', context)

@login_required
@permission_required('assets.add_asset', raise_exception=True)
def asset_create(request):
    """Create a new asset."""
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.created_by = request.user
            # Ensure subcategory is correctly assigned (it's handled by the form validation now)
            # asset.subcategory = form.cleaned_data['subcategory'] 
            asset.save()
            messages.success(request, f"تمت إضافة الأصل '{asset.name}' بنجاح.")
            return redirect('assets:asset_list')
        else:
            messages.error(request, "الرجاء تصحيح الأخطاء أدناه.")
    else:
        form = AssetForm()
        
    context = {
        'title': 'إضافة أصل جديد',
        'form': form,
        'is_new': True
    }
    return render(request, 'assets/asset_form.html', context)

@login_required
def asset_detail(request, pk):
    """Display details for a specific asset."""
    asset = get_object_or_404(Asset.objects.select_related('subcategory__category', 'location', 'custodian', 'created_by'), pk=pk)
    context = {
        'title': f'تفاصيل الأصل: {asset.name}',
        'asset': asset
    }
    return render(request, 'assets/asset_detail.html', context)

@login_required
@permission_required('assets.change_asset', raise_exception=True)
def asset_update(request, pk):
    """Update an existing asset."""
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, f"تم تعديل الأصل '{asset.name}' بنجاح.")
            return redirect('assets:asset_detail', pk=asset.pk)
        else:
            messages.error(request, "الرجاء تصحيح الأخطاء أدناه.")
    else:
        form = AssetForm(instance=asset)
        
    context = {
        'title': f'تعديل الأصل: {asset.name}',
        'form': form,
        'asset': asset,
        'is_new': False
    }
    return render(request, 'assets/asset_form.html', context)

@login_required
@permission_required('assets.delete_asset', raise_exception=True)
def asset_delete(request, pk):
    """Delete an asset (handle POST request)."""
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        asset_name = asset.name
        try:
            asset.delete()
            messages.success(request, f"تم حذف الأصل '{asset_name}' بنجاح.")
            return redirect('assets:asset_list')
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء حذف الأصل: {e}")
            return redirect('assets:asset_detail', pk=pk)
    else:
        # If accessed via GET, redirect to detail view or show confirmation page
        # For simplicity, redirecting back to detail view
        return redirect('assets:asset_detail', pk=pk)


# --- Excel Import Views --- 

@login_required
@permission_required('assets.add_asset', raise_exception=True) # Assuming import requires add permission
def import_excel(request):
    """Step 1: Upload Excel file."""
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            importer = ExcelImporter()
            file_path = importer.save_uploaded_file(excel_file)
            df, error = importer.read_excel_file(file_path)
            
            if error:
                messages.error(request, f"خطأ في قراءة ملف Excel: {error}")
                os.remove(file_path) # Clean up temp file
                return redirect('assets:import_excel')
            
            excel_columns = importer.get_excel_columns(df)
            request.session['import_file_path'] = file_path
            request.session['excel_columns'] = excel_columns
            
            # Store DataFrame in session (consider alternatives for large files)
            # For simplicity, storing path and re-reading later if needed, or storing serialized df
            # df.to_csv(file_path + '.csv', index=False) # Example: save as CSV temporarily
            # request.session['temp_csv_path'] = file_path + '.csv'
            
            return redirect('assets:import_excel_mapping')
    else:
        form = ExcelUploadForm()
        
    context = {
        'title': 'استيراد الأصول من Excel - الخطوة 1: رفع الملف',
        'form': form
    }
    return render(request, 'assets/import_excel.html', context)

@login_required
@permission_required('assets.add_asset', raise_exception=True)
def import_excel_mapping(request):
    """Step 2: Map Excel columns to asset fields."""
    file_path = request.session.get('import_file_path')
    excel_columns = request.session.get('excel_columns')
    
    if not file_path or not excel_columns:
        messages.error(request, "لم يتم العثور على بيانات الملف. يرجى البدء من جديد.")
        return redirect('assets:import_excel')
        
    importer = ExcelImporter()
    required_fields = importer.field_mapping # Use the defined mapping
    
    if request.method == 'POST':
        column_mapping = {}
        for field, _ in required_fields.items():
            column_mapping[field] = request.POST.get(f'map_{field}')
            
        # Basic validation: Check if essential fields are mapped
        missing_required = importer.validate_mapping(column_mapping)
        if missing_required:
             messages.error(request, f"الحقول التالية مطلوبة ولم يتم تحديد عمود لها: {', '.join(missing_required)}")
             # Re-render the mapping form with error
             context = {
                'title': 'استيراد الأصول من Excel - الخطوة 2: مطابقة الأعمدة',
                'excel_columns': excel_columns,
                'required_fields': required_fields,
                'current_mapping': column_mapping # Pass current mapping back to template
             }
             return render(request, 'assets/import_excel_mapping.html', context)

        request.session['column_mapping'] = column_mapping
        return redirect('assets:import_excel_preview')
        
    context = {
        'title': 'استيراد الأصول من Excel - الخطوة 2: مطابقة الأعمدة',
        'excel_columns': excel_columns,
        'required_fields': required_fields,
        'current_mapping': {} # Initial empty mapping
    }
    return render(request, 'assets/import_excel_mapping.html', context)

@login_required
@permission_required('assets.add_asset', raise_exception=True)
def import_excel_preview(request):
    """Step 3: Preview data and validate."""
    file_path = request.session.get('import_file_path')
    column_mapping = request.session.get('column_mapping')
    
    if not file_path or not column_mapping:
        messages.error(request, "لم يتم العثور على بيانات الملف أو المطابقة. يرجى البدء من جديد.")
        return redirect('assets:import_excel')
        
    importer = ExcelImporter()
    df, error = importer.read_excel_file(file_path)
    if error:
        messages.error(request, f"خطأ في قراءة ملف Excel: {error}")
        return redirect('assets:import_excel')
        
    preview_data = importer.preview_data(df, column_mapping)
    validation_errors = importer.validate_data(df, column_mapping)
    
    if request.method == 'POST':
        if validation_errors:
            messages.error(request, "توجد أخطاء في البيانات. يرجى مراجعة الملف الأصلي وتصحيحه ثم إعادة المحاولة.")
            # Optionally delete temp file here or keep for debugging
            # os.remove(file_path)
            # del request.session['import_file_path']
            # del request.session['column_mapping']
            # del request.session['excel_columns']
            # return redirect('assets:import_excel')
        else:
            # Proceed with actual import
            try:
                success_count, failure_count, failures = importer.process_import(df, column_mapping, request.user)
                messages.success(request, f"تم استيراد {success_count} أصل بنجاح.")
                if failure_count > 0:
                    messages.warning(request, f"فشل استيراد {failure_count} سجل. التفاصيل: {failures}") # Improve failure reporting
                
                # Clean up session and temp file
                os.remove(file_path)
                del request.session['import_file_path']
                del request.session['column_mapping']
                del request.session['excel_columns']
                
                return redirect('assets:asset_list')
            except Exception as e:
                messages.error(request, f"حدث خطأ غير متوقع أثناء عملية الاستيراد: {e}")
                # Optionally clean up session/file here too
                return redirect('assets:import_excel_preview') # Stay on preview page on error

    context = {
        'title': 'استيراد الأصول من Excel - الخطوة 3: معاينة وتأكيد',
        'preview_data': preview_data,
        'validation_errors': validation_errors,
        'has_errors': bool(validation_errors)
    }
    return render(request, 'assets/import_excel_preview.html', context)


# --- Depreciation Views --- 

@login_required
@permission_required('assets.manage_depreciation', raise_exception=True)
def depreciation_management(request):
    """Manage asset depreciation."""
    # Placeholder: Fetch relevant data for display
    context = {
        'title': 'إدارة الإهلاك'
    }
    return render(request, 'assets/depreciation_management.html', context)

@login_required
@permission_required('assets.manage_depreciation', raise_exception=True)
def calculate_depreciation(request):
    """Calculate depreciation for assets (Placeholder)."""
    # Placeholder: Add actual depreciation calculation logic here
    messages.success(request, 'تم حساب الإهلاك بنجاح (وظيفة تحت الإنشاء).')
    return redirect('assets:depreciation_management')

@login_required
@permission_required('assets.manage_depreciation', raise_exception=True)
def post_depreciation(request):
    """Post depreciation entries (Placeholder)."""
    # Placeholder: Add actual depreciation posting logic here
    messages.success(request, 'تم ترحيل قيود الإهلاك بنجاح (وظيفة تحت الإنشاء).')
    return redirect('assets:depreciation_management')


# --- Transfer Views --- 

@login_required
def transfer_list(request):
    """Display a list of all transfers."""
    transfers = AssetTransfer.objects.select_related('asset', 'from_location', 'from_custodian', 'to_location', 'to_custodian').all()
    context = {
        'title': 'قائمة نقل الأصول',
        'transfers': transfers
    }
    return render(request, 'assets/transfer_list.html', context)

@login_required
@permission_required("assets.add_assettransfer", raise_exception=True) # Use correct permission
def transfer_create(request):
    """Create a new asset transfer."""
    if request.method == 'POST':
        form = AssetTransferForm(request.POST)
        if form.is_valid():
            transfer = form.save(commit=False)
            asset = transfer.asset
            
            # Store old location/custodian before updating
            transfer.from_location = asset.location
            transfer.from_custodian = asset.custodian
            
            # Update asset's location and custodian
            asset.location = transfer.to_location
            asset.custodian = transfer.to_custodian
            # Optionally update asset status if needed, e.g., asset.status = 'transferred'
            # However, the model has 'transferred' status, let's update it.
            # asset.status = 'transferred' # Let's keep it active, transfer just changes location/custodian
            asset.save()
            
            transfer.created_by = request.user
            transfer.save()
            
            messages.success(request, f"تم نقل الأصل '{asset.name}' بنجاح إلى {transfer.to_location} بعهدة {transfer.to_custodian}.")
            return redirect('assets:transfer_list')
        else:
            messages.error(request, "الرجاء تصحيح الأخطاء أدناه.")
    else:
        form = AssetTransferForm()
        
    context = {
        'title': 'نقل أصل جديد',
        'form': form
    }
    return render(request, 'assets/transfer_form.html', context)

@login_required
def transfer_detail(request, pk):
    """Display details for a specific transfer."""
    transfer = get_object_or_404(AssetTransfer.objects.select_related('asset', 'from_location', 'from_custodian', 'to_location', 'to_custodian', 'created_by'), pk=pk)
    context = {
        'title': f'تفاصيل نقل الأصل: {transfer.asset.code}',
        'transfer': transfer
    }
    return render(request, 'assets/transfer_detail.html', context)

# Update/Delete views for Transfer would follow a similar pattern


# --- Disposal Views --- 

@login_required
def disposal_list(request):
    """Display a list of all disposals."""
    disposals = AssetDisposal.objects.select_related('asset').all()
    context = {
        'title': 'قائمة استبعاد الأصول',
        'disposals': disposals
    }
    return render(request, 'assets/disposal_list.html', context)

@login_required
@permission_required("assets.add_assetdisposal", raise_exception=True) # Use correct permission
def disposal_create(request):
    """Create a new asset disposal record."""
    if request.method == 'POST':
        form = AssetDisposalForm(request.POST)
        if form.is_valid():
            disposal = form.save(commit=False)
            asset = disposal.asset
            
            # Set book value at disposal (can be calculated or fetched)
            # For simplicity, let's use the current net book value
            disposal.book_value_at_disposal = asset.net_book_value 
            
            # Update asset status
            asset.status = 'disposed'
            asset.save()
            
            disposal.created_by = request.user
            disposal.save()
            
            messages.success(request, f"تم استبعاد الأصل 	'{asset.name}' بنجاح.")
            return redirect('assets:disposal_list')
        else:
            messages.error(request, "الرجاء تصحيح الأخطاء أدناه.")
    else:
        form = AssetDisposalForm()
        
    context = {
        'title': 'استبعاد أصل جديد',
        'form': form
    }
    return render(request, 'assets/disposal_form.html', context)

@login_required
def disposal_detail(request, pk):
    """Display details for a specific disposal."""
    disposal = get_object_or_404(AssetDisposal.objects.select_related('asset', 'created_by'), pk=pk)
    context = {
        'title': f'تفاصيل استبعاد الأصل: {disposal.asset.code}',
        'disposal': disposal
    }
    return render(request, 'assets/disposal_detail.html', context)

# Update/Delete views for Disposal would follow a similar pattern


# --- HTMX Helper View --- 

@login_required
def load_subcategories(request):
    """Load subcategories based on selected category for HTMX request."""
    category_id = request.GET.get('category')
    subcategories = AssetSubcategory.objects.filter(category_id=category_id).order_by('name')
    options = '<option value="">---------</option>'
    for subcategory in subcategories:
        options += f'<option value="{subcategory.pk}">{subcategory.name}</option>'
    # Return just the options part for HTMX to swap into the select element
    return HttpResponse(options)


