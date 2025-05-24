from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required

@login_required
def asset_report(request):
    """Generate asset report."""
    context = {
        'title': 'تقرير الأصول',
        'assets': []  # Placeholder - would be fetched from actual data
    }
    return render(request, 'reports/asset_report.html', context)

@login_required
def depreciation_report(request):
    """Generate depreciation report."""
    context = {
        'title': 'تقرير الإهلاك',
        'depreciation_entries': []  # Placeholder - would be fetched from actual data
    }
    return render(request, 'reports/asset_report.html', context)

@login_required
def transfer_report(request):
    """Generate transfer report."""
    context = {
        'title': 'تقرير نقل الأصول',
        'transfers': []  # Placeholder - would be fetched from actual data
    }
    return render(request, 'reports/asset_report.html', context)

@login_required
def disposal_report(request):
    """Generate disposal report."""
    context = {
        'title': 'تقرير استبعاد الأصول',
        'disposals': []  # Placeholder - would be fetched from actual data
    }
    return render(request, 'reports/asset_report.html', context)

@login_required
def acquisition_report(request):
    """Generate acquisition report."""
    context = {
        'title': 'تقرير اقتناء الأصول',
        'acquisitions': []  # Placeholder - would be fetched from actual data
    }
    return render(request, 'reports/asset_report.html', context)
