from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    """Display the main dashboard."""
    context = {
        'title': 'لوحة التحكم',
        'total_assets': 0,  # Placeholder - would be calculated from actual data
        'total_depreciation': 0,  # Placeholder - would be calculated from actual data
        'recent_transfers': [],  # Placeholder - would be fetched from actual data
        'recent_disposals': [],  # Placeholder - would be fetched from actual data
    }
    return render(request, 'dashboard/index.html', context)
