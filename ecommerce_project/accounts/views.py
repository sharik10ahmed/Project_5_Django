import random

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.contrib import messages

from .models import EmailOTP


def register_view(request):

    if request.method == 'POST':

        full_name = request.POST['full_name']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register')

        user = User.objects.create_user(
            username=email,
            first_name=full_name,
            email=email,
            password=password
        )

        otp = str(random.randint(100000, 999999))

        EmailOTP.objects.create(
            user=user,
            otp=otp
        )

        send_mail(
            'Email Verification OTP',
            f'Your OTP is {otp}',
            'your_email@gmail.com',
            [email],
            fail_silently=False,
        )

        request.session['email'] = email

        return redirect('verify_otp')

    return render(request, 'accounts/register.html')


def verify_otp(request):

    email = request.session.get('email')

    if request.method == 'POST':

        otp = request.POST['otp']

        user = User.objects.get(username=email)

        otp_obj = EmailOTP.objects.get(user=user)

        if otp_obj.otp == otp:

            otp_obj.is_verified = True
            otp_obj.save()

            send_mail(
                'Welcome To Our Website',
                'Your email has been verified successfully.',
                'your_email@gmail.com',
                [email],
                fail_silently=False,
            )

            login(request, user)

            return redirect('home')

        else:
            messages.error(request, 'Invalid OTP')

    return render(request, 'accounts/verify_otp.html')


def login_view(request):

    if request.method == 'POST':

        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(
            username=email,
            password=password
        )

        if user:

            login(request, user)

            return redirect('home')

        else:

            messages.error(request, 'Invalid Credentials')

    return render(request, 'accounts/login.html')


def logout_view(request):

    logout(request)

    return redirect('login')


def profile_view(request):

    return render(request, 'accounts/profile.html')