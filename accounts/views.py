from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.urls import reverse

def login(request):
  if request.method == "POST":
    username = request.POST['id']
    password = request.POST['password']
    user = auth.authenticate(request, username=username, password=password)
    if user is not None:
      auth.login(request, user)
      return redirect(reverse('index'))
    return render(request, 'login.html')
  return render(request, 'login.html')

def signup(request):
  if request.method == "POST":
    if request.POST["password"] == request.POST["password-confirm"]:
      user = User.objects.create_user(
        username=request.POST["id"],password=request.POST["password"]
      )
      auth.login(request, user)
      return redirect(reverse('index'))
    return render(request, 'signup.html')

  return render(request, 'signup.html')    
# Create your views here.
