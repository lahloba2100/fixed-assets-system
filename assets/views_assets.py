from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.management import call_command
from django.db import transaction

from .models import Asset, DepreciationEntry
from .forms import AssetForm

class AssetListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Asset
    template_name = 'assets/asset_list.html'
    context_object_name = 'assets'
    permission_required = 'assets.view_asset'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by location if provided
        location = self.request.GET.get('location')
        if location:
            queryset = queryset.filter(location_id=location)
            
        # Filter by group1 if provided
        group1 = self.request.GET.get('group1')
        if group1:
            queryset = queryset.filter(group1_id=group1)
            
        # Filter by group2 if provided
        group2 = self.request.GET.get('group2')
        if group2:
            queryset = queryset.filter(group2_id=group2)
            
        return queryset

class AssetDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Asset
    template_name = 'assets/asset_detail.html'
    context_object_name = 'asset'
    permission_required = 'assets.view_asset'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['depreciation_entries'] = self.object.depreciation_entries.all().order_by('-entry_date')
        return context

class AssetCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = 'assets/asset_form.html'
    success_url = reverse_lazy('assets:asset_list')
    permission_required = 'assets.add_asset'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class AssetUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = 'assets/asset_form.html'
    success_url = reverse_lazy('assets:asset_list')
    permission_required = 'assets.change_asset'

def calculate_depreciation_view(request):
    """
    View for calculating depreciation
    """
    if not request.user.has_perm('assets.add_depreciationentry'):
        messages.error(request, 'ليس لديك صلاحية لحساب الإهلاك')
        return redirect('assets:depreciation_management')
    
    if request.method == 'POST':
        month = int(request.POST.get('month', timezone.now().month))
        year = int(request.POST.get('year', timezone.now().year))
        
        try:
            # Call the management command
            call_command('calculate_depreciation', month=month, year=year)
            messages.success(request, f'تم حساب الإهلاك بنجاح لشهر {month}/{year}')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حساب الإهلاك: {str(e)}')
    
    return redirect('assets:depreciation_management')

def post_depreciation_view(request):
    """
    View for posting depreciation entries
    """
    if not request.user.has_perm('assets.post_depreciationentry'):
        messages.error(request, 'ليس لديك صلاحية لترحيل قيود الإهلاك')
        return redirect('assets:depreciation_management')
    
    if request.method == 'POST':
        entry_ids = request.POST.getlist('entry_ids')
        
        if not entry_ids:
            messages.error(request, 'لم يتم تحديد أي قيود للترحيل')
            return redirect('assets:depreciation_management')
        
        try:
            with transaction.atomic():
                now = timezone.now()
                count = 0
                
                for entry_id in entry_ids:
                    entry = DepreciationEntry.objects.get(id=entry_id)
                    if not entry.posted:
                        entry.posted = True
                        entry.posted_at = now
                        entry.posted_by = request.user
                        entry.save()
                        count += 1
                
                messages.success(request, f'تم ترحيل {count} قيد بنجاح')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء ترحيل القيود: {str(e)}')
    
    return redirect('assets:depreciation_management')

def depreciation_management_view(request):
    """
    View for depreciation management
    """
    if not request.user.has_perm('assets.view_depreciationentry'):
        messages.error(request, 'ليس لديك صلاحية لعرض قيود الإهلاك')
        return redirect('home')
    
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    unposted_entries = DepreciationEntry.objects.filter(posted=False).order_by('-entry_date')
    
    context = {
        'current_month': current_month,
        'current_year': current_year,
        'unposted_entries': unposted_entries,
    }
    
    return render(request, 'assets/depreciation_management.html', context)
