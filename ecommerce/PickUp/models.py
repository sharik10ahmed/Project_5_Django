from django.db import models

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

    def __str__(self):
        return self.name


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