from django.shortcuts import render, redirect
from django.urls import reverse

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

import random

from django.core.mail import send_mail

from .models import User, Category, Product, Gallery, TeamMember, ContactMessage, ContactConfig, Cart, CartItem, Wishlist, Order, OrderItem

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

                "Login Successful"

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

    messages.success(request,"Logged Out Successfully")

    return redirect('login')

def product(request):
    products = Product.objects.filter(is_active=True)
    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist_product_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    
    return render(
        request,
        'product.html',
        {
            'products': products,
            'wishlist_product_ids': wishlist_product_ids
        }
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




@login_required(login_url='login')
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})


@login_required(login_url='login')
def cart(request):
    cart_obj, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart.html', {'cart': cart_obj})


@login_required(login_url='login')
def checkout(request):
    cart_obj, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart_obj.items.all()
    if not cart_items.exists():
        messages.error(request, "Your cart is empty. Add products before checking out.")
        return redirect('cart')
    
    if request.method == 'POST':
        # 1. Verify stock levels
        for item in cart_items:
            if item.quantity > item.product.quantity:
                messages.error(request, f"Sorry, '{item.product.name}' only has {item.product.quantity} units left in stock. Please adjust your cart.")
                return redirect('cart')
        
        # 2. Extract billing details
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        alternate_phone = request.POST.get('alternate_phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        
        # 3. Create Order
        order = Order.objects.create(
            user=request.user,
            name=name,
            phone=phone,
            alternate_phone=alternate_phone,
            email=email,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            total_price=cart_obj.get_total_price()
        )
        
        # 4. Create OrderItems & Decrement Stock
        for item in cart_items:
            price = item.product.discount_price if item.product.discount_price else item.product.price
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=price
            )
            # Decrement product stock
            item.product.quantity -= item.quantity
            item.product.save()
            
        # 5. Clear cart
        cart_items.delete()
        
        messages.success(request, "Order Placed Successfully! Your items will be shipped soon.")
        return redirect('orders')
        
    return render(request, 'checkout.html', {
        'cart': cart_obj,
        'cart_items': cart_items,
    })


def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to add products to the cart.")
        return redirect(f"{reverse('login')}?next={request.path}")
    
    product_obj = Product.objects.filter(id=product_id, is_active=True).first()
    if not product_obj:
        messages.error(request, "Product not found or inactive.")
        return redirect('product')
        
    if product_obj.quantity <= 0:
        messages.error(request, "This product is currently out of stock.")
        return redirect(request.META.get('HTTP_REFERER', 'product'))
        
    cart_obj, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart_obj, product=product_obj)
    
    if not item_created:
        if cart_item.quantity + 1 > product_obj.quantity:
            messages.error(request, f"Cannot add more of this item. Only {product_obj.quantity} available in stock.")
            return redirect(request.META.get('HTTP_REFERER', 'product'))
        cart_item.quantity += 1
        cart_item.save()
    else:
        if product_obj.quantity < 1:
            messages.error(request, "This product is currently out of stock.")
            cart_item.delete()
            return redirect(request.META.get('HTTP_REFERER', 'product'))
            
    messages.success(request, f"Added '{product_obj.name}' to your cart.")
    return redirect(request.META.get('HTTP_REFERER', 'product'))


@login_required(login_url='login')
def remove_from_cart(request, item_id):
    cart_item = CartItem.objects.filter(id=item_id, cart__user=request.user).first()
    if cart_item:
        product_name = cart_item.product.name
        cart_item.delete()
        messages.success(request, f"Removed '{product_name}' from your cart.")
    return redirect('cart')


@login_required(login_url='login')
def update_cart_quantity(request, item_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        cart_item = CartItem.objects.filter(id=item_id, cart__user=request.user).first()
        if cart_item:
            product_qty = cart_item.product.quantity
            if action == 'increase':
                if cart_item.quantity + 1 <= product_qty:
                    cart_item.quantity += 1
                    cart_item.save()
                    messages.success(request, "Quantity increased.")
                else:
                    messages.error(request, f"Only {product_qty} items available in stock.")
            elif action == 'decrease':
                if cart_item.quantity - 1 > 0:
                    cart_item.quantity -= 1
                    cart_item.save()
                    messages.success(request, "Quantity decreased.")
                else:
                    cart_item.delete()
                    messages.success(request, "Item removed from cart.")
    return redirect('cart')


def add_to_wishlist(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to add products to your wishlist.")
        return redirect(f"{reverse('login')}?next={request.path}")
        
    product_obj = Product.objects.filter(id=product_id, is_active=True).first()
    if not product_obj:
        messages.error(request, "Product not found or inactive.")
        return redirect('product')
        
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product_obj).first()
    if wishlist_item:
        wishlist_item.delete()
        messages.success(request, f"Removed '{product_obj.name}' from your wishlist.")
    else:
        Wishlist.objects.create(user=request.user, product=product_obj)
        messages.success(request, f"Added '{product_obj.name}' to your wishlist.")
        
    return redirect(request.META.get('HTTP_REFERER', 'product'))


@login_required(login_url='login')
def remove_from_wishlist(request, wishlist_id):
    wishlist_item = Wishlist.objects.filter(id=wishlist_id, user=request.user).first()
    if wishlist_item:
        product_name = wishlist_item.product.name
        wishlist_item.delete()
        messages.success(request, f"Removed '{product_name}' from your wishlist.")
    return redirect('wishlist')




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




@login_required(login_url='login')
def orders(request):
    user_orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')
    return render(request, 'orders.html', {'orders': user_orders})


@login_required(login_url='login')
def cancel_order(request, order_id):
    order = Order.objects.filter(id=order_id, user=request.user).first()
    if not order:
        messages.error(request, "Order not found.")
        return redirect('orders')
        
    if order.status == 'Pending':
        # Restore product stock
        for item in order.items.all():
            item.product.quantity += item.quantity
            item.product.save()
            
        order.status = 'Cancelled'
        order.save()
        messages.success(request, f"Order #PKU-{order.id} has been cancelled successfully.")
    else:
        messages.error(request, f"Order #PKU-{order.id} cannot be cancelled as its status is '{order.status}'. Only pending orders can be cancelled.")
        
    return redirect('orders')

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


def contact(request):
    # Fetch configuration or supply defaults
    config = ContactConfig.objects.first()
    if not config:
        # Create a transient default config object if not in database
        config = ContactConfig(
            platform_rating=4.9,
            max_rating=5,
            reviews_count="200+",
            whatsapp_number="+1234567890",
            whatsapp_text="Hello, I have a question about PickUp",
            visit_title="VISIT US",
            visit_text="123 Main Street, Suite 400, New York, NY 10001",
            visit_icon="bi bi-geo-alt-fill",
            call_title="CALL US",
            call_text="+1 (555) 123-4567\n+1 (555) 765-4321",
            call_icon="bi bi-telephone-fill",
            email_title="EMAIL US",
            email_text="support@pickup.com\nsales@pickup.com",
            email_icon="bi bi-envelope-fill",
            hours_title="STORE HOURS",
            hours_text="Mon - Fri: 9:00 AM - 8:00 PM\nSat - Sun: 10:00 AM - 6:00 PM",
            hours_icon="bi bi-clock-fill",
            map_iframe='<iframe src="https://maps.google.com/maps?q=india&t=&z=5&ie=UTF8&iwloc=&output=embed" width="100%" height="150" style="border:0;" loading="lazy"></iframe>'
        )

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if not name or not email or not message:
            messages.error(request, "All fields (Name, Email, Message) are required.")
        else:
            ContactMessage.objects.create(name=name, email=email, message=message)
            messages.success(request, f"Thank you, {name}! Your message has been sent successfully.")
            return redirect('contact')

    visit_lines = [line.strip() for line in config.visit_text.split('\n') if line.strip()]
    call_lines = [line.strip() for line in config.call_text.split('\n') if line.strip()]
    email_lines = [line.strip() for line in config.email_text.split('\n') if line.strip()]
    hours_lines = [line.strip() for line in config.hours_text.split('\n') if line.strip()]

    # Make stars listing
    rating_val = float(config.platform_rating)
    full_stars = int(rating_val)
    half_star = 1 if (rating_val - full_stars) >= 0.25 else 0
    empty_stars = config.max_rating - full_stars - half_star
    stars = {
        'full': range(full_stars),
        'half': range(half_star),
        'empty': range(empty_stars)
    }

    # Generate WhatsApp URL
    whatsapp_clean_num = ''.join(c for c in config.whatsapp_number if c.isdigit() or c == '+')
    import urllib.parse
    whatsapp_encoded_text = urllib.parse.quote(config.whatsapp_text)
    whatsapp_url = f"https://wa.me/{whatsapp_clean_num.replace('+', '')}?text={whatsapp_encoded_text}"

    context = {
        'config': config,
        'visit_lines': visit_lines,
        'call_lines': call_lines,
        'email_lines': email_lines,
        'hours_lines': hours_lines,
        'stars': stars,
        'whatsapp_url': whatsapp_url,
    }

    return render(request, 'contact.html', context)