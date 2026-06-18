from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Category



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
