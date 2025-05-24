from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.urls import reverse

@login_required
@permission_required('auth.view_user', raise_exception=True)
def user_list(request):
    """Display a list of all users."""
    users = User.objects.all()
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
@permission_required('auth.add_user', raise_exception=True)
def user_create(request):
    """Create a new user."""
    # Placeholder function - in a real implementation, this would handle form submission
    return render(request, 'accounts/user_form.html', {'user': None})

@login_required
@permission_required('auth.view_user', raise_exception=True)
def user_detail(request, pk):
    """Display details for a specific user."""
    user = get_object_or_404(User, pk=pk)
    return render(request, 'accounts/user_detail.html', {'user': user})

@login_required
@permission_required('auth.change_user', raise_exception=True)
def user_update(request, pk):
    """Update an existing user."""
    # Placeholder function - in a real implementation, this would handle form submission
    user = get_object_or_404(User, pk=pk)
    return render(request, 'accounts/user_form.html', {'user': user})

@login_required
@permission_required('auth.change_user', raise_exception=True)
def user_activate(request, pk):
    """Activate a user account."""
    user = get_object_or_404(User, pk=pk)
    user.is_active = True
    user.save()
    messages.success(request, f'User {user.username} has been activated.')
    return redirect('accounts:user_list')

@login_required
@permission_required('auth.change_user', raise_exception=True)
def user_deactivate(request, pk):
    """Deactivate a user account."""
    user = get_object_or_404(User, pk=pk)
    user.is_active = False
    user.save()
    messages.success(request, f'User {user.username} has been deactivated.')
    return redirect('accounts:user_list')
