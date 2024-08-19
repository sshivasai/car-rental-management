from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponseRedirect
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, ProfilePictureUpdateSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login_page')
        else:
            for field, error in serializer.errors.items():
                messages.error(request, f"{field}: {error[0]}")
            return redirect('register_page')

def register_page(request):
    return render(request, 'users/register.html')

class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return redirect('profile')
            messages.error(request, "Invalid Password/Username. Please try again.")
        else:
            for field, error in serializer.errors.items():
                messages.error(request, f"{field}: {error[0]}")
        return redirect('login_page')

def login_page(request):
    return render(request, 'users/login.html')

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

def profile_page(request):
    if not request.user.is_authenticated:
        return redirect('login_page')
    return render(request, 'users/profile.html', {'user': request.user})

def update_profile_picture(request):
    if request.method == 'POST':
        user = request.user
        profile_picture = request.FILES.get('profile_picture')
        
        if profile_picture:
            user.profile_picture = profile_picture
            user.save()
            messages.success(request, "Profile picture updated successfully.")
            return HttpResponseRedirect('/users/profile/')  # Redirect to the profile page
        
        messages.error(request, "No profile picture found in the request.")
        return HttpResponseRedirect('/users/profile/')
    
    return HttpResponseRedirect('/users/profile/')