from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

from .models import User





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

        mobile_no = request.POST['mobile_no']

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




        mobile_no = request.POST['mobile_no']
        
        user = User.objects.create_user(


            username=username,


            email=email,


            full_name=full_name,

            mobile_no=mobile_no,


            password=password


        )



        user.save()



        messages.success(

            request,

            "Registration successful"

        )


        return redirect('login')




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

    messages.success(
        request,
        "Logged out successfully"
    )

    return redirect('login')