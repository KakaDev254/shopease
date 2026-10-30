from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegisterForm, LoginForm, ProfileUpdateForm


# ------------------------------------------------------------------
# REGISTER
# ------------------------------------------------------------------
def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email'].strip().lower()
            user.first_name = form.cleaned_data['first_name'].strip()
            user.last_name = form.cleaned_data['last_name'].strip()
            user.save()
            login(request, user)
            messages.success(request, f'Welcome to ShopEase, {user.first_name}!')
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


# ------------------------------------------------------------------
# LOGIN
# ------------------------------------------------------------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')

            # Safe redirect to ?next= (prevents open-redirect attacks)
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect('home')
    else:
        form = LoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


# ------------------------------------------------------------------
# LOGOUT
# ------------------------------------------------------------------
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ------------------------------------------------------------------
# PROFILE
# ------------------------------------------------------------------
@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {
        'user_obj': request.user,
    })


@login_required
def profile_update(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile_update.html', {'form': form})


# ------------------------------------------------------------------
# ORDER HISTORY (placeholder — hook up Order model when ready)
# ------------------------------------------------------------------
@login_required
def order_history(request):
    orders = []  # replace with Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/orders.html', {'orders': orders})