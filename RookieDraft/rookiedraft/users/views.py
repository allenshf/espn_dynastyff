from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm

#User Registration Page
def register(request):

    #If form was sent, validate
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 'Your account has been created!')
            return redirect('login')
    #Else, display user registration form
    else: 
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

#Profile page
@login_required
def profile(request):
    return render(request, 'users/profile.html')