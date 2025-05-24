from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

@login_required
def asset_list(request):
    """Display a list of all assets."""
    context = {
        'title': 'قائمة الأصول',
        'assets': []  # Placeholder - would be fetched from actual data
    }
    return render(request, 'assets/asset_list.html', context)

@login_required
@permission_required('assets.add_asset', raise_exception=True)
def asset_create(request):
    """Create a new asset."""
    context = {
        'title': 'إضافة أصل جديد'
    }
    return render(request, 'assets/asset_detail.html', context)

@login_required
def asset_detail(request, pk):
    """Display details for a specific asset."""
    context = {
        'title': 'تفاصيل الأصل',
        'asset': {}  # Placeholder - would be fetched from actual data
    }
    return render(request, 'assets/asset_detail.html', context)

@login_required
@permission_required('assets.change_asset', raise_exception=True)
def asset_update(request, pk):
    """Update an existing asset."""
    context = {
        'title': 'تعديل الأصل',
        'asset': {}  # Placeholder - would be fetched from actual data
    }
    return render(request, 'assets/asset_detail.html', context)

@login_required
def import_excel(request):
    """Import assets from Excel file."""
    context = {
        'title': 'استيراد من Excel'
    }
    return render(request, 'assets/import_excel.html', context)

@login_required
def import_excel_mapping(request):
    """Map Excel columns to asset fields."""
    context = {
        'title': 'مطابقة أعمدة Excel'
    }
    return render(request, 'assets/import_excel_mapping.html', context)

@login_required
def import_excel_preview(request):
    """Preview data before import."""
    context = {
        'title': 'معاينة البيانات قبل الاستيراد'
    }
    return render(request, 'assets/import_excel_preview.html', context)

@login_required
@permission_required('assets.manage_depreciation', raise_exception=True)
def depreciation_management(request):
    """Manage asset depreciation."""
    context = {
        'title': 'إدارة الإهلاك'
    }
    return render(request, 'assets/depreciation_management.html', context)

@login_required
@permission_required('assets.manage_depreciation', raise_exception=True)
def calculate_depreciation(request):
    """Calculate depreciation for assets."""
    messages.success(request, 'تم حساب الإهلاك بنجاح.')
    return redirect('assets:depreciation_management')

@login_required
@permission_required('assets.manage_depreciation', raise_exception=True)
def post_depreciation(request):
    """Post depreciation entries."""
    messages.success(request, 'تم ترحيل قيود الإهلاك بنجاح.')
    return redirect('assets:depreciation_management')

@login_required
def transfer_list(request):
    """Display a list of all transfers."""
    context = {
        'title': 'قائمة نقل الأصول',
        'transfers': []  # Placeholder - would be fetched from actual data
    }
    return render(request, 'assets/transfer_list.html', context)

@login_required
@permission_required('assets.add_transfer', raise_exception=True)
def transfer_create(request):
    """Create a new transfer."""
    context = {
        'title': 'نقل أصل جديد'
    }
    return render(request, 'assets/transfer_list.html', context)

@login_required
def transfer_detail(request, pk):
    """Display details for a specific transfer."""
    context = {
        'title': 'تفاصيل نقل الأصل',
        'transfer': {}  # Placeholder - would be fetched from actual data
    }
    return render(request, 'assets/transfer_list.html', context)

@login_required
@permission_required('assets.change_transfer', raise_exception=True)
def transfer_update(request, pk):
    """Update an existing transfer."""
    context = {
        'title': 'تعديل نقل الأصل',
        'transfer': {}  # Placeholder - would be fetched from actual data
    }
    return render(request, 'assets/transfer_list.html', context)

@login_required
def disposal_list(request):
    """Display a list of all disposals."""
    context = {
        'title': 'قائمة استبعاد الأصول',
        'disposals': []  # Placeholder - would be fetched from actual data
    }
    return render(request, 'assets/disposal_list.html', context)

@login_required
@permission_required('assets.add_disposal', raise_exception=True)
def disposal_create(request):
    """Create a new disposal."""
    context = {
        'title': 'استبعاد أصل جديد'
    }
    return render(request, 'assets/disposal_list.html', context)

@login_required
def disposal_detail(request, pk):
    """Display details for a specific disposal."""
    context = {
        'title': 'تفاصيل استبعاد الأصل',
        'disposal': {}  # Placeholder - would be fetched from actual data
    }
    return render(request, 'assets/disposal_list.html', context)

@login_required
@permission_required('assets.change_disposal', raise_exception=True)
def disposal_update(request, pk):
    """Update an existing disposal."""
    context = {
        'title': 'تعديل استبعاد الأصل',
        'disposal': {}  # Placeholder - would be fetched from actual data
    }
    return render(request, 'assets/disposal_list.html', context)
