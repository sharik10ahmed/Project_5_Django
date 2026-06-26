from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Category, Product, Announcement, Gallery, TeamMember, ContactMessage, ContactConfig



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


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'message', 'created_at')

    def has_add_permission(self, request):
        return False  # Messages should only come from front-end submissions


@admin.register(ContactConfig)
class ContactConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'platform_rating', 'reviews_count', 'whatsapp_number')
    fieldsets = (
        ('Platform Rating Info', {
            'fields': ('platform_rating', 'max_rating', 'reviews_count')
        }),
        ('WhatsApp Quick Connect', {
            'fields': ('whatsapp_number', 'whatsapp_text')
        }),
        ('Google Map Location', {
            'fields': ('map_iframe',)
        }),
        ('Visit Us Card', {
            'fields': ('visit_title', 'visit_icon', 'visit_text')
        }),
        ('Call Us Card', {
            'fields': ('call_title', 'call_icon', 'call_text')
        }),
        ('Email Us Card', {
            'fields': ('email_title', 'email_icon', 'email_text')
        }),
        ('Store Hours Card', {
            'fields': ('hours_title', 'hours_icon', 'hours_text')
        }),
    )

    def has_add_permission(self, request):
        # Allow only one configuration row to exist
        return not ContactConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of the configuration
        return False