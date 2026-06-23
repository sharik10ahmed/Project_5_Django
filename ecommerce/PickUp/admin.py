from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Category, Product, Announcement, Gallery, TeamMember



@admin.register(User)

class CustomUserAdmin(UserAdmin):


    model = User


    list_display = (
        'username',
        'email',
        'full_name',
        'mobile_no',
        'gender',
        'is_staff',
        'is_active'

    )



    list_filter = (

        'is_staff',
        'is_active',
        'gender'

    )



    search_fields = (

        'email',
        'full_name',
        'mobile_no'

    )



    ordering = (

        'email',

    )




    fieldsets = (

        (
            None,
            {
                'fields':(

                    'email',
                    'password'

                )
            }
        ),



        (
            'Personal Information',
            {

                'fields':(

                    'full_name',
                    'mobile_no',
                    'alternate_mobile_no',
                    'dob',
                    'gender',
                    'address',
                    'profile_image'

                )

            }

        ),



        (
            'Permissions',
            {

                'fields':(

                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions'

                )

            }

        ),


    )




    add_fieldsets = (

        (

            None,

            {

                'classes':(
                    'wide',
                ),

                'fields':(

                    'email',
                    'full_name',
                    'mobile_no',
                    'password1',
                    'password2',
                    'is_active',
                    'is_staff'

                )

            }

        ),

    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    model = Category

    list_display = (
        'name',
        'slug',
        'is_active',
        'created_at'
    )

    list_filter = (
        'is_active',
        'created_at'
    )

    search_fields = (
        'name',
        'description'
    )

    ordering = (
        'name',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }

    fieldsets = (
        (
            'Category Information',
            {
                'fields': (
                    'name',
                    'slug',
                    'description',
                    'image',
                    'is_active'
                )
            }
        ),
    )

    readonly_fields = (
        'created_at',
        'updated_at'
    )

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    model = Product

    list_display = (
        'name',
        'category',
        'price',
        'discount_price',
        'quantity',
        'is_active',
        'created_at'
    )

    list_filter = (
        'is_active',
        'category',
        'created_at'
    )

    search_fields = (
        'name',
        'description'
    )

    ordering = (
        '-created_at',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }

    fieldsets = (
        (
            'Product Information',
            {
                'fields': (
                    'name',
                    'slug',
                    'category',
                    'description',
                    'image'
                )
            }
        ),
        (
            'Pricing',
            {
                'fields': (
                    'price',
                    'discount_price'
                )
            }
        ),
        (
            'Stock',
            {
                'fields': (
                    'quantity',
                )
            }
        ),
        (
            'Status',
            {
                'fields': (
                    'is_active',
                )
            }
        ),
    )

    readonly_fields = (
        'created_at',
        'updated_at'
    )

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):

    model = Announcement

    list_display = (
        'heading',
        'is_active',
        'created_at'
    )

    list_filter = (
        'is_active',
        'created_at'
    )

    search_fields = (
        'heading',
        'description'
    )

    ordering = (
        '-created_at',
    )

    fieldsets = (
        (
            'Announcement Content',
            {
                'fields': (
                    'heading',
                    'description',
                    'icon'
                )
            }
        ),
        (
            'Status',
            {
                'fields': (
                    'is_active',
                )
            }
        ),
    )

    readonly_fields = (
        'created_at',
        'updated_at'
    )

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):

    model = Gallery

    list_display = (
        'title',
        'order',
        'is_active',
        'created_at'
    )

    list_filter = (
        'is_active',
        'created_at'
    )

    search_fields = (
        'title',
        'description'
    )

    ordering = (
        'order',
        '-created_at'
    )

    fieldsets = (
        (
            'Gallery Item',
            {
                'fields': (
                    'title',
                    'description',
                    'image',
                    'image_file',
                    'order'
                )
            }
        ),
        (
            'Status',
            {
                'fields': (
                    'is_active',
                )
            }
        ),
    )

    readonly_fields = (
        'created_at',
        'updated_at'
    )

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):

    model = TeamMember

    list_display = (
        'name',
        'role',
        'order',
        'is_active',
        'created_at'
    )

    list_filter = (
        'is_active',
        'created_at'
    )

    search_fields = (
        'name',
        'role',
        'email'
    )

    ordering = (
        'order',
    )

    fieldsets = (
        (
            'Basic Information',
            {
                'fields': (
                    'name',
                    'role',
                    'image',
                    'bio'
                )
            }
        ),
        (
            'Contact Information',
            {
                'fields': (
                    'email',
                    'phone'
                )
            }
        ),
        (
            'Social Links',
            {
                'fields': (
                    'linkedin',
                    'twitter'
                )
            }
        ),
        (
            'Settings',
            {
                'fields': (
                    'order',
                    'is_active'
                )
            }
        ),
    )

    readonly_fields = (
        'created_at',
        'updated_at'
    )