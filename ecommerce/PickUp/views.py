from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

import random

from django.core.mail import send_mail

from .models import User, Category, Product, Gallery, TeamMember

from .forms import UserProfileForm

from django.contrib.auth.decorators import login_required




# Home Page

def home(request):

    return render(
        request,
        'home.html'
    )





# Register Page
def register(request):

    if request.method == "POST":


        full_name = request.POST['full_name']

        email = request.POST['email']

        password = request.POST['password']

        password2 = request.POST['password2']




        if password != password2:


            messages.error(
                request,
                "Password does not match"
            )
            
            
            return redirect('register')






        if User.objects.filter(email=email).exists():


            messages.error(
                request,
                "Email already registered"
            )


            return redirect('register')





        # username from email

        username = email.split('@')[0]



        # check username exists

        if User.objects.filter(username=username).exists():

            username = username + "1"






        # OTP Generate

        otp = random.randint(100000,999999)






        # Store data temporarily in session

        request.session['register_data'] = {


            'username': username,


            'full_name': full_name,


            'email': email,


            'password': password,


            'otp': otp


        }





        # Send OTP Email

        send_mail(

        subject="Verify Your PickUp Account - OTP",
        
        message=f"""

Hello {full_name},


Welcome to PickUp 🛒


Thank you for choosing PickUp.


To complete your account registration, please verify your email address using the OTP below:


━━━━━━━━━━━━━━━━━━

        {otp}

━━━━━━━━━━━━━━━━━━


Please do not share this OTP with anyone.


If you did not request this registration, please ignore this email.



Thank you for joining PickUp.


Best Regards,

PickUp Team

Your trusted shopping partner


""",


        from_email=None,


        recipient_list=[email]

        )

        return redirect('verify_otp')

    return render(request,'register.html')






# Login

def login_view(request):

    if request.method == "POST":


        login_input = request.POST['login_input']

        password = request.POST['password']



        # Check email or username

        user = None


        if '@' in login_input:


            try:

                user_obj = User.objects.get(
                    email=login_input
                )


                user = authenticate(

                    request,

                    username=user_obj.username,

                    password=password

                )


            except User.DoesNotExist:

                user = None



        else:


            user = authenticate(

                request,

                username=login_input,

                password=password

            )





        if user is not None:


            login(
                request,
                user
            )


            messages.success(

                request,

                "Login successful"

            )


            return redirect('home')




        else:


            messages.error(

                request,

                "Invalid username/email or password"

            )


            return redirect('login')





    return render(request,'login.html')

def logout_view(request):

    logout(request)

    messages.success(request,"Logged out successfully")

    return redirect('login')

def product(request):

    products = Product.objects.filter(is_active=True)

    return render(
        request,
        'product.html',
        {'products': products}
    )




def category(request):

    categories = Category.objects.filter(is_active=True)

    return render(
        request,
        'category.html',
        {'categories': categories}
    )




def gallery(request):

    gallery_items = Gallery.objects.filter(is_active=True)

    return render(
        request,
        'gallery.html',
        {'gallery_items': gallery_items}
    )




def about(request):

    team_members = TeamMember.objects.filter(is_active=True)

    return render(request, 'about.html', {'team_members': team_members})




def wishlist(request):

    return render(request,'wishlist.html')



def cart(request):

    return render(request,'cart.html')




def profile(request):

    return render(request,'profile.html')


@login_required(login_url='login')
def edit_profile(request):

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect('edit_profile')

    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})




def orders(request):

    return render(request,'orders.html')

def privacy_policy(request):

    return render(request, 'privacy_policy.html')

def refund_policy(request):

    return render(request, 'refund_policy.html')

def shipping_policy(request):

    return render(request, 'shipping_policy.html')

def terms_and_conditions(request):

    return render(request, 'terms_and_conditions.html')

def our_mission(request):

    return render(request, 'our_mission.html')

def our_vision(request):

    return render(request, 'our_vision.html')

def verify_otp(request):


    if request.method=="POST":


        entered_otp = request.POST['otp']


        data = request.session.get('register_data')



        if data and str(data['otp']) == entered_otp:



          



            user = User.objects.create_user(

                username=data['username'],

                email=data['email'],


                full_name=data['full_name'],


                password=data['password']


            )



            user.save()





            send_mail(


               subject="Welcome to PickUp - Registration Successful",


                message=f"""

Hello {data['full_name']},


🎉 Welcome to PickUp!


Your account has been successfully created.


Account Details:


Name: {data['full_name']}

Email: {data['email']}



You can now login and start shopping with PickUp.


Thank you for becoming a part of PickUp.


Warm Regards,

PickUp Team

Your trusted ecommerce destination

""",


                from_email=None,


                recipient_list=[data['email']]


            )





            del request.session['register_data']



            messages.success(

                request,

                "Registration successful. Please login."

            )


            return redirect('login')





        else:


            messages.error(

                request,

                "Invalid OTP"

            )



    return render(request,'verify_otp.html')