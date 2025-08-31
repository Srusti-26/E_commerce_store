from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from store.models import Order

@login_required
def profile(request):
    """Display and update user profile."""
    if request.method == 'POST':
        # Update user information
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('users:profile')
    
    return render(request, 'users/profile.html')

@login_required
def order_history(request):
    """Display user's order history."""
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'users/order_history.html', {'orders': orders})