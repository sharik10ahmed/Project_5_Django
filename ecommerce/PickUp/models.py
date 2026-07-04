from django.db import models
from django.utils.text import slugify

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)



# Custom User Manager

class UserManager(BaseUserManager):


    def create_user(
        self,
        username,
        email,
        full_name,
        password=None
    ):


        if not email:
            raise ValueError("Email is required")
        

        email = self.normalize_email(email)


        user = self.model(

            username=username,

            email=email,

            full_name=full_name,
            
        )


        user.set_password(password)


        user.save(
            using=self._db
        )


        return user




    def create_superuser(
        self,
        username,
        email,
        full_name,
        password=None
    ):


        user = self.create_user(

            username,

            email,

            full_name,

            password

        )


        user.is_staff = True

        user.is_superuser = True

        user.is_active = True



        user.save(using=self._db)
        return user





# Custom User Model


class User(AbstractBaseUser,PermissionsMixin):


    GENDER_CHOICES = (

        ('Male','Male'),

        ('Female','Female'),

        ('Other','Other'),

    )



    username = models.CharField(

        max_length=50,

        unique=True

    )



    full_name = models.CharField(

        max_length=100

    )



    email = models.EmailField(

        unique=True

    )



    mobile_no = models.CharField(

        max_length=15,

        unique=True,

         blank=True,

         null=True

    )



    alternate_mobile_no = models.CharField(

        max_length=15,

        blank=True,

        null=True

    )



    dob = models.DateField(

        blank=True,

        null=True

    )



    address = models.TextField(

        blank=True,

        null=True

    )



    profile_image = models.ImageField(

        upload_to='profile/',

        blank=True,

        null=True

    )



    gender = models.CharField(

        max_length=10,

        choices=GENDER_CHOICES,

        blank=True,

        null=True

    )



    is_active = models.BooleanField(

        default=True

    )



    is_staff = models.BooleanField(

        default=False

    )



    created_at = models.DateTimeField(

        auto_now_add=True

    )



    updated_at = models.DateTimeField(

        auto_now=True

    )




    objects = UserManager()



    USERNAME_FIELD = "username"



    REQUIRED_FIELDS = [

        "email",

        "full_name",

        "mobile_no"

    ]




    def __str__(self):

        return self.username


# Category Model

class Category(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


# Product Model

class Product(models.Model):

    sku = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    name = models.CharField(
        max_length=255,
        unique=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
        null=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    quantity = models.IntegerField(
        default=0
    )

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name_plural = "Products"
        ordering = ['-created_at']

    def _generate_sku(self):
        if self.category_id:
            prefix = slugify(self.category.name or self.category.slug or 'product')[:4].upper() or 'PROD'
        else:
            prefix = 'PROD'

        base_sku = f"{prefix}-{self.pk:05d}" if self.pk else f"{prefix}-00000"
        sku = base_sku
        suffix = 1

        while Product.objects.filter(sku=sku).exclude(pk=self.pk).exists():
            sku = f"{base_sku}-{suffix}"
            suffix += 1

        return sku

    def save(self, *args, **kwargs):
        if not self.sku:
            if self.pk:
                self.sku = self._generate_sku()
            else:
                super().save(*args, **kwargs)
                self.sku = self._generate_sku()
                super().save(update_fields=['sku'])
                return

        super().save(*args, **kwargs)

    def __str__(self):
        if self.sku:
            return f"{self.name} {self.sku}"
        return self.name


class Feedback(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    customer_name = models.CharField(max_length=100, default='Anonymous User')
    review_title = models.CharField(max_length=255, blank=True, null=True)
    customer_message = models.TextField()
    stars = models.PositiveSmallIntegerField(default=5)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Feedback'

    @property
    def star_icons(self):
        return range(self.stars)

    def __str__(self):
        return f"{self.product.name} - {self.stars} stars"


class Inventory(Product):
    class Meta:
        proxy = True
        verbose_name_plural = 'Inventory'


# Announcement Model

class Announcement(models.Model):

    heading = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    icon = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default='bi bi-truck',
        help_text='Bootstrap icon class (e.g., bi bi-truck, bi bi-star-fill)'
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name_plural = "Announcements"
        ordering = ['-created_at']

    def __str__(self):
        return self.heading


# Gallery Model

class Gallery(models.Model):

    title = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    image = models.URLField(
        blank=True,
        null=True,
        help_text='URL of the gallery image'
    )

    image_file = models.ImageField(
        upload_to='gallery/',
        blank=True,
        null=True,
        help_text='Upload image file alternatively'
    )

    is_active = models.BooleanField(
        default=True
    )

    order = models.IntegerField(
        default=0,
        help_text='Display order in gallery'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name_plural = "Gallery"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


# Team Member Model

class TeamMember(models.Model):

    name = models.CharField(
        max_length=255
    )

    role = models.CharField(
        max_length=255,
        help_text='Job title or position'
    )

    bio = models.TextField(
        blank=True,
        null=True,
        help_text='Brief bio of the team member'
    )

    image = models.ImageField(
        upload_to='team/',
        blank=True,
        null=True
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    linkedin = models.URLField(
        blank=True,
        null=True
    )

    twitter = models.URLField(
        blank=True,
        null=True
    )

    order = models.IntegerField(
        default=0,
        help_text='Display order on page'
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name_plural = "Team Members"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"Message from {self.name} ({self.email})"


class ContactConfig(models.Model):
    # Rating Info
    platform_rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.9, help_text="Rating of Platform (e.g. 4.9)")
    max_rating = models.IntegerField(default=5, help_text="Max rating scale (e.g. 5)")
    reviews_count = models.CharField(max_length=50, default="200+", help_text="Number of customer reviews (e.g. 200+)")
    
    # WhatsApp Info
    whatsapp_number = models.CharField(max_length=20, default="+1234567890", help_text="WhatsApp phone number with country code")
    whatsapp_text = models.CharField(max_length=255, default="Hello, I have a question about PickUp", help_text="Default message text for WhatsApp")

    # Card 1 - Visit Us
    visit_title = models.CharField(max_length=100, default="VISIT US")
    visit_text = models.TextField(default="123 Main Street, Suite 400, New York, NY 10001")
    visit_icon = models.CharField(max_length=50, default="bi bi-geo-alt-fill")

    # Card 2 - Call Us
    call_title = models.CharField(max_length=100, default="CALL US")
    call_text = models.TextField(default="+1 (555) 123-4567\n+1 (555) 765-4321")
    call_icon = models.CharField(max_length=50, default="bi bi-telephone-fill")

    # Card 3 - Email Us
    email_title = models.CharField(max_length=100, default="EMAIL US")
    email_text = models.TextField(default="support@pickup.com\nsales@pickup.com")
    email_icon = models.CharField(max_length=50, default="bi bi-envelope-fill")

    # Card 4 - Store Hours
    hours_title = models.CharField(max_length=100, default="STORE HOURS")
    hours_text = models.TextField(default="Mon - Fri: 9:00 AM - 8:00 PM\nSat - Sun: 10:00 AM - 6:00 PM")
    hours_icon = models.CharField(max_length=50, default="bi bi-clock-fill")

    # Google Map Embed Code
    map_iframe = models.TextField(
        default='<iframe src="https://maps.google.com/maps?q=india&t=&z=5&ie=UTF8&iwloc=&output=embed" width="100%" height="150" style="border:0;" loading="lazy"></iframe>',
        help_text="Embed iframe code for Google Maps location"
    )

    class Meta:
        verbose_name = "Contact Page Configuration"
        verbose_name_plural = "Contact Page Configuration"

    def __str__(self):
        return "Contact Page Config"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def get_subtotal(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def get_delivery_charge(self):
        subtotal = self.get_subtotal()
        if subtotal >= 500 or subtotal == 0:
            return 0
        return 200

    def get_total_price(self):
        return self.get_subtotal() + self.get_delivery_charge()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_subtotal(self):
        if self.product.discount_price:
            return self.product.discount_price * self.quantity
        return self.product.price * self.quantity


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Order(models.Model):
    STATUS_CHOICES = (
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    alternate_phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    tracking_number = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Confirmed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.id})"

    def get_subtotal(self):
        return self.price * self.quantity