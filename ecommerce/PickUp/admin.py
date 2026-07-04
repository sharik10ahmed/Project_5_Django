from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html

from .models import User, Category, Product, Inventory, Announcement, Gallery, TeamMember, ContactMessage, ContactConfig, Cart, CartItem, Wishlist, Order, OrderItem, Feedback



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
        'product_with_sku',
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
        'sku',
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
        'sku',
        'created_at',
        'updated_at'
    )

    def product_with_sku(self, obj):
        if obj.sku:
            return f'{obj.name} {obj.sku}'
        return obj.name

    product_with_sku.short_description = 'Product Name'


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'stars', 'status', 'action')
    list_filter = ('status', 'stars', 'created_at')
    search_fields = ('product__name', 'customer_message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/approve/', self.admin_site.admin_view(self.approve_feedback), name='feedback-approve'),
            path('<int:object_id>/reject/', self.admin_site.admin_view(self.reject_feedback), name='feedback-reject'),
        ]
        return custom_urls + urls

    def product_name(self, obj):
        return obj.product.name

    product_name.short_description = 'Product Name'

    def action(self, obj):
        view_link = format_html('<a href="{}">View</a>', reverse('admin:PickUp_feedback_change', args=[obj.pk]))
        approve_link = format_html('<a href="{}">Approve</a>', reverse('admin:feedback-approve', args=[obj.pk]))
        reject_link = format_html('<a href="{}">Reject</a>', reverse('admin:feedback-reject', args=[obj.pk]))
        return format_html('{} | {} | {}', view_link, approve_link, reject_link)

    action.short_description = 'Action'

    def approve_feedback(self, request, object_id):
        feedback = get_object_or_404(Feedback, pk=object_id)
        feedback.status = 'Approved'
        feedback.save(update_fields=['status'])
        messages.success(request, f'Feedback for {feedback.product.name} approved.')
        return HttpResponseRedirect(reverse('admin:PickUp_feedback_changelist'))

    def reject_feedback(self, request, object_id):
        feedback = get_object_or_404(Feedback, pk=object_id)
        feedback.status = 'Pending'
        feedback.save(update_fields=['status'])
        messages.success(request, f'Feedback for {feedback.product.name} marked as pending.')
        return HttpResponseRedirect(reverse('admin:PickUp_feedback_changelist'))


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    model = Inventory

    list_display = ('image_thumbnail', 'product_with_sku', 'quantity', 'action')
    search_fields = ('name', 'sku')
    list_filter = ('is_active', 'category')
    ordering = ('name',)

    readonly_fields = ('sku',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:object_id>/adjust-stock/',
                self.admin_site.admin_view(self.adjust_stock_view),
                name='inventory-adjust-stock',
            ),
        ]
        return custom_urls + urls

    def product_with_sku(self, obj):
        if obj.sku:
            return f'{obj.name} {obj.sku}'
        return obj.name

    product_with_sku.short_description = 'Product Name'

    def image_thumbnail(self, obj):
        if obj.image and getattr(obj.image, 'url', None):
            return format_html(
                '<img src="{}" alt="{}" style="width:60px;height:60px;object-fit:cover;border-radius:4px;" />',
                obj.image.url,
                obj.name,
            )
        return '-'

    image_thumbnail.short_description = 'Image'

    def adjust_stock_view(self, request, object_id):
        product = get_object_or_404(Product, pk=object_id)
        qty_value = request.GET.get('qty', '1')

        try:
            qty_value = int(qty_value)
        except (TypeError, ValueError):
            qty_value = 1

        if qty_value < 1:
            qty_value = 1

        if request.GET.get('action') == 'subtract':
            new_quantity = max(0, product.quantity - qty_value)
            action_label = 'removed from'
        else:
            new_quantity = product.quantity + qty_value
            action_label = 'added to'

        product.quantity = new_quantity
        product.save(update_fields=['quantity'])

        messages.success(
            request,
            f'Stock {action_label} {product.name} is now {product.quantity}.',
        )
        return HttpResponseRedirect(reverse('admin:PickUp_inventory_changelist'))

    def action(self, obj):
        return format_html(
            '<div style="display:flex;gap:4px;align-items:center;">'
            '<input type="number" id="qty_{id}" value="1" min="1" style="width:60px;" />'
            '<button type="button" onclick="window.location.href=\'{id}/adjust-stock/?action=add&qty=\' + document.getElementById(\'qty_{id}\').value;" title="Add stock">+</button>'
            '<button type="button" onclick="window.location.href=\'{id}/adjust-stock/?action=subtract&qty=\' + document.getElementById(\'qty_{id}\').value;" title="Subtract stock">-</button>'
            '</div>',
            id=obj.id,
        )

    action.short_description = 'Action'


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


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    inlines = [CartItemInline]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__name')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'phone', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'phone', 'email', 'user__username')
    inlines = [OrderItemInline]
    readonly_fields = ('user', 'total_price', 'created_at')
    list_editable = ('status',)