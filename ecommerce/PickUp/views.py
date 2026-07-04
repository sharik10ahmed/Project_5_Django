from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q, Avg
from django.views import View
from django.http import HttpResponse
from django.template.loader import render_to_string

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

import random

from django.core.mail import send_mail

import logging


logger = logging.getLogger(__name__)

from .models import User, Category, Product, Gallery, TeamMember, ContactMessage, ContactConfig, Cart, CartItem, Wishlist, Order, OrderItem, Feedback
from .email_utils import send_order_success_email

from .forms import UserProfileForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin




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
    import razorpay
    from django.conf import settings

    cart_obj, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart_obj.items.all()
    if not cart_items.exists():
        messages.error(request, "Your cart is empty. Add products before checking out.")
        return redirect('cart')
    
    total_price = cart_obj.get_total_price()
    amount_in_paise = int(total_price * 100)

    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

    if request.method == 'POST':
        # 1. Verify stock levels
        for item in cart_items:
            if item.quantity > item.product.quantity:
                messages.error(request, f"Sorry, '{item.product.name}' only has {item.product.quantity} units left in stock. Please adjust your cart.")
                return redirect('cart')
        
        # 2. Extract Razorpay response fields
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        
        payment_fields_present = bool(razorpay_payment_id or razorpay_order_id or razorpay_signature)
        if payment_fields_present and not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
            messages.error(request, "Payment failed or was not completed. Please try again.")
            return redirect('checkout')

        if payment_fields_present:
            try:
                client.utility.verify_payment_signature({
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_signature': razorpay_signature
                })
            except Exception as e:
                messages.error(request, f"Payment verification failed: {str(e)}")
                return redirect('checkout')

        # 4. Extract billing details
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        alternate_phone = request.POST.get('alternate_phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        
        # 5. Create Order
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
            total_price=total_price
        )
        
        # 6. Create OrderItems & Decrement Stock
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
            
        # 7. Clear cart
        cart_items.delete()
        
        # 8. Send Confirmation Email & Payment Receipt
        send_order_success_email(order, razorpay_payment_id)
        
        messages.success(request, "Order Placed Successfully! Your receipt has been emailed to you.")
        return redirect('order_detail', order.id)
        
    # GET Request: Initialize Razorpay order for the checkout modal popup
    razorpay_order_id = None
    if amount_in_paise > 0:
        try:
            razorpay_order = client.order.create({
                "amount": amount_in_paise,
                "currency": "INR",
                "payment_capture": 1
            })
            razorpay_order_id = razorpay_order['id']
        except Exception as e:
            messages.warning(request, f"Could not initialize Razorpay: {str(e)}. Proceeding with fallback mode.")
            razorpay_order_id = None

    return render(request, 'checkout.html', {
        'cart': cart_obj,
        'cart_items': cart_items,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_key_id': settings.RAZORPAY_API_KEY,
        'razorpay_amount': amount_in_paise,
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
        
    qty_to_add = 1
    if request.method == 'POST':
        try:
            qty_to_add = int(request.POST.get('quantity', 1))
            if qty_to_add < 1:
                qty_to_add = 1
        except ValueError:
            qty_to_add = 1
            
    cart_obj, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart_obj, product=product_obj)
    
    if not item_created:
        if cart_item.quantity + qty_to_add > product_obj.quantity:
            messages.error(request, f"Cannot add more of this item. Only {product_obj.quantity} available in stock.")
            return redirect(request.META.get('HTTP_REFERER', 'product'))
        cart_item.quantity += qty_to_add
        cart_item.save()
    else:
        if qty_to_add > product_obj.quantity:
            messages.error(request, f"Cannot add that quantity. Only {product_obj.quantity} available in stock.")
            cart_item.delete()
            return redirect(request.META.get('HTTP_REFERER', 'product'))
        cart_item.quantity = qty_to_add
        cart_item.save()
            
    messages.success(request, f"Added '{product_obj.name}' (Quantity: {qty_to_add}) to your cart.")
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




def get_user_orders_queryset(request):
    queryset = (
        Order.objects.filter(user=request.user)
        .prefetch_related('items__product')
        .order_by('-created_at')
    )

    query = request.GET.get('q', '').strip() or request.GET.get('query', '').strip()
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()
    product_name = request.GET.get('product_name', '').strip()

    if query:
        try:
            order_id = int(query)
        except ValueError:
            order_id = None

        if order_id is not None:
            queryset = queryset.filter(Q(id=order_id) | Q(tracking_number__icontains=query))
        else:
            queryset = queryset.filter(Q(tracking_number__icontains=query))

    if start_date:
        queryset = queryset.filter(created_at__date__gte=start_date)

    if end_date:
        queryset = queryset.filter(created_at__date__lte=end_date)

    if product_name:
        queryset = queryset.filter(items__product__name__icontains=product_name)

    active_filters = {
        'q': query,
        'query': query,
        'start_date': start_date,
        'end_date': end_date,
        'product_name': product_name,
    }

    return queryset.distinct(), active_filters


class MyOrdersView(LoginRequiredMixin, View):
    login_url = 'login'
    template_name = 'my_orders.html'

    def get(self, request, *args, **kwargs):
        queryset, active_filters = get_user_orders_queryset(request)
        return render(request, self.template_name, {
            'orders': queryset,
            'active_filters': active_filters,
        })


my_orders = MyOrdersView.as_view()


@login_required(login_url='login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})


@login_required(login_url='login')
def invoice_preview(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
        'items': order.items.all(),
        'reference_id': f'PKU-{order.id}',
        'customer_name': order.name,
        'delivery_address': f"{order.address}\n{order.city}, {order.state} - {order.pincode}",
        'email': order.email,
        'phone': order.phone,
        'alt_phone': order.alternate_phone or 'N/A',
        'total_cost': order.total_price,
    }
    return render(request, 'invoice_template.html', context)


@login_required(login_url='login')
def invoice_download(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
        'items': order.items.all(),
        'reference_id': f'PKU-{order.id}',
        'customer_name': order.name,
        'delivery_address': f"{order.address}\n{order.city}, {order.state} - {order.pincode}",
        'email': order.email,
        'phone': order.phone,
        'alt_phone': order.alternate_phone or 'N/A',
        'total_cost': order.total_price,
    }
    html_string = render_to_string('invoice_template.html', context)

    from xhtml2pdf import pisa

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
    pisa_status = pisa.CreatePDF(html_string, dest=response)

    if pisa_status.err:
        return HttpResponse('PDF generation failed', status=500)

    return response


@login_required(login_url='login')
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'Confirmed':
        for item in order.items.all():
            item.product.quantity += item.quantity
            item.product.save()

        order.status = 'Cancelled'
        order.save()
        messages.success(request, f'Order #PKU-{order.id} has been cancelled successfully.')
    else:
        messages.info(request, f'Order #PKU-{order.id} is already {order.status.lower()}.')
    return redirect('my_orders')


@login_required(login_url='login')
def order_delete(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.delete()
    messages.success(request, 'Order successfully deleted.')
    return redirect('my_orders')


@login_required(login_url='login')
def orders(request):
    queryset, active_filters = get_user_orders_queryset(request)
    return render(request, 'orders.html', {
        'orders': queryset,
        'active_filters': active_filters,
    })


@login_required(login_url='login')
def cancel_order(request, order_id):
    order = Order.objects.filter(id=order_id, user=request.user).first()
    if not order:
        messages.error(request, "Order not found.")
        return redirect('orders')
        
    if order.status == 'Confirmed':
        # Restore product stock
        for item in order.items.all():
            item.product.quantity += item.quantity
            item.product.save()
            
        order.status = 'Cancelled'
        order.save()
        messages.success(request, f"Order #PKU-{order.id} has been cancelled successfully.")
    else:
        messages.error(request, f"Order #PKU-{order.id} cannot be cancelled as its status is '{order.status}'. Only confirmed orders can be cancelled.")
        
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


def product_detail(request, product_id):
    product_obj = Product.objects.filter(id=product_id, is_active=True).first()
    if not product_obj:
        messages.error(request, "Product not found or inactive.")
        return redirect('product')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to submit a review.')
            return redirect(f"{reverse('login')}?next={reverse('product_detail', args=[product_obj.id])}")

        customer_name = getattr(request.user, 'get_full_name', lambda: None)() or getattr(request.user, 'full_name', None) or request.user.username
        customer_message = request.POST.get('customer_message', '').strip()
        review_title = request.POST.get('review_title', '').strip()
        stars_value = request.POST.get('stars', '5').strip()

        if customer_message:
            try:
                stars = int(stars_value)
            except (TypeError, ValueError):
                stars = 5

            Feedback.objects.create(
                product=product_obj,
                customer_name=customer_name,
                review_title=review_title or None,
                customer_message=customer_message,
                stars=max(1, min(5, stars)),
                status='Pending'
            )
            messages.success(request, 'Your feedback has been submitted and is pending approval.')
        else:
            messages.error(request, 'Please enter a review message before submitting.')

        return redirect('product_detail', product_id=product_obj.id)

    feedbacks = Feedback.objects.filter(product=product_obj, status='Approved').order_by('-created_at')
    total_reviews = feedbacks.count()
    average_rating = round(feedbacks.aggregate(Avg('stars'))['stars__avg'] or 0, 1)
    average_rating_percentage = (average_rating / 5) * 100 if average_rating else 0

    star_percentages = {}
    for star_level in range(5, 0, -1):
        count = feedbacks.filter(stars=star_level).count()
        percentage = round((count / total_reviews) * 100, 1) if total_reviews else 0
        star_percentages[star_level] = percentage

    in_wishlist = False
    wishlist_product_ids = []
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product_obj).exists()
        wishlist_product_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))

    # Get related products (same category, excluding this one)
    related_products = Product.objects.filter(category=product_obj.category, is_active=True).exclude(id=product_obj.id)[:4]

    # If less than 4, fill with other active products
    related_count = related_products.count()
    if related_count < 4:
        fill_products = Product.objects.filter(is_active=True).exclude(id=product_obj.id).exclude(id__in=[p.id for p in related_products])[:4 - related_count]
        related_products = list(related_products) + list(fill_products)

    return render(
        request,
        'product_detail.html',
        {
            'product': product_obj,
            'feedbacks': feedbacks,
            'total_reviews': total_reviews,
            'average_rating': average_rating,
            'average_rating_percentage': average_rating_percentage,
            'star_percentages': star_percentages,
            'in_wishlist': in_wishlist,
            'wishlist_product_ids': wishlist_product_ids,
            'related_products': related_products,
        }
    )


def buy_now(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to purchase products.")
        return redirect(f"{reverse('login')}?next={reverse('product_detail', args=[product_id])}")
    
    product_obj = Product.objects.filter(id=product_id, is_active=True).first()
    if not product_obj:
        messages.error(request, "Product not found or inactive.")
        return redirect('product')
        
    if product_obj.quantity <= 0:
        messages.error(request, "This product is currently out of stock.")
        return redirect(request.META.get('HTTP_REFERER', 'product'))
        
    qty_to_add = 1
    if request.method == 'POST':
        try:
            qty_to_add = int(request.POST.get('quantity', 1))
            if qty_to_add < 1:
                qty_to_add = 1
        except ValueError:
            qty_to_add = 1
            
    cart_obj, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart_obj, product=product_obj)
    
    if not item_created:
        if qty_to_add > product_obj.quantity:
            messages.error(request, f"Only {product_obj.quantity} available in stock.")
            return redirect(request.META.get('HTTP_REFERER', 'product'))
        cart_item.quantity = qty_to_add
        cart_item.save()
    else:
        if qty_to_add > product_obj.quantity:
            messages.error(request, f"Only {product_obj.quantity} available in stock.")
            cart_item.delete()
            return redirect(request.META.get('HTTP_REFERER', 'product'))
        cart_item.quantity = qty_to_add
        cart_item.save()
        
    messages.success(request, f"Proceeding to checkout with '{product_obj.name}'.")
    return redirect('checkout')