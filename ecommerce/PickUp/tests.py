from django.test import TestCase
from django.urls import reverse
from .models import ContactMessage, ContactConfig

class ContactUsTests(TestCase):
    def setUp(self):
        # Clear existing configs to avoid duplicates in test DB
        ContactConfig.objects.all().delete()
        self.config = ContactConfig.objects.create(
            platform_rating=4.8,
            reviews_count="150+",
            whatsapp_number="+919876543210",
            whatsapp_text="Hi PickUp!",
            visit_title="VISIT US",
            visit_text="123 PickUp Blvd",
            call_title="CALL US",
            call_text="+91-1234567890",
            email_title="EMAIL US",
            email_text="contact@pickup.com",
            hours_title="STORE HOURS",
            hours_text="9 AM - 6 PM"
        )

    def test_contact_page_get(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact.html')
        self.assertContains(response, '123 PickUp Blvd')
        self.assertContains(response, 'contact@pickup.com')
        self.assertContains(response, '4.8')
        self.assertContains(response, '150+')
        self.assertContains(response, '919876543210')

    def test_contact_page_post_success(self):
        post_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Hello, testing the contact form!'
        }
        response = self.client.post(reverse('contact'), data=post_data)
        self.assertRedirects(response, reverse('contact'))
        
        # Verify message was saved to database
        self.assertEqual(ContactMessage.objects.count(), 1)
        msg = ContactMessage.objects.first()
        self.assertEqual(msg.name, 'John Doe')
        self.assertEqual(msg.email, 'john@example.com')
        self.assertEqual(msg.message, 'Hello, testing the contact form!')

    def test_contact_page_post_validation(self):
        post_data = {
            'name': '',
            'email': 'john@example.com',
            'message': ''
        }
        response = self.client.post(reverse('contact'), data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)


from .models import Cart, CartItem, Wishlist, Product, Category, User

class CartAndWishlistTests(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            full_name='Test User',
            password='testpassword'
        )
        
        # Create category
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        
        # Create products
        self.product1 = Product.objects.create(
            name='Test Phone',
            slug='test-phone',
            category=self.category,
            price=10000.00,
            quantity=5,
            is_active=True
        )
        
        self.product_out_of_stock = Product.objects.create(
            name='Out Of Stock TV',
            slug='oos-tv',
            category=self.category,
            price=50000.00,
            quantity=0,
            is_active=True
        )

    def test_product_sku_is_generated_when_missing(self):
        product = Product.objects.create(
            name='Wireless Mouse',
            slug='wireless-mouse',
            category=self.category,
            price=999.00,
            quantity=3,
            is_active=True
        )

        self.assertTrue(product.sku)
        self.assertTrue(product.sku.startswith('ELEC') or product.sku.startswith('ELECT'))
        self.assertEqual(product.sku, f"{product.sku.split('-')[0]}-{product.pk:05d}")

    def test_anonymous_user_cannot_add_to_cart(self):
        response = self.client.get(reverse('add_to_cart', args=[self.product1.id]))
        # Should redirect to login
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('add_to_cart', args=[self.product1.id]))
        self.assertEqual(CartItem.objects.count(), 0)

    def test_anonymous_user_cannot_add_to_wishlist(self):
        response = self.client.get(reverse('add_to_wishlist', args=[self.product1.id]))
        # Should redirect to login
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('add_to_wishlist', args=[self.product1.id]))
        self.assertEqual(Wishlist.objects.count(), 0)

    def test_authenticated_user_can_add_to_cart(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('add_to_cart', args=[self.product1.id]))
        self.assertEqual(response.status_code, 302)
        
        # Verify CartItem created
        self.assertEqual(CartItem.objects.count(), 1)
        cart_item = CartItem.objects.first()
        self.assertEqual(cart_item.product, self.product1)
        self.assertEqual(cart_item.quantity, 1)

    def test_authenticated_user_cannot_add_more_than_stock(self):
        self.client.login(username='testuser', password='testpassword')
        # Add 5 items (product quantity is 5)
        for i in range(5):
            self.client.get(reverse('add_to_cart', args=[self.product1.id]))
        
        # Verify quantity is 5
        cart_item = CartItem.objects.first()
        self.assertEqual(cart_item.quantity, 5)
        
        # Attempt to add the 6th item
        response = self.client.get(reverse('add_to_cart', args=[self.product1.id]))
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)

    def test_authenticated_user_cannot_add_out_of_stock_product(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('add_to_cart', args=[self.product_out_of_stock.id]))
        self.assertEqual(CartItem.objects.count(), 0)

    def test_authenticated_user_can_add_to_wishlist(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('add_to_wishlist', args=[self.product1.id]))
        self.assertEqual(response.status_code, 302)
        
        # Verify Wishlist item created
        self.assertEqual(Wishlist.objects.count(), 1)
        wishlist_item = Wishlist.objects.first()
        self.assertEqual(wishlist_item.product, self.product1)

    def test_anonymous_user_cannot_access_checkout(self):
        response = self.client.get(reverse('checkout'))
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('checkout'))

    def test_authenticated_user_empty_cart_redirects_to_cart(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('checkout'))
        self.assertRedirects(response, reverse('cart'))

    def test_authenticated_user_with_items_can_access_and_submit_checkout(self):
        self.client.login(username='testuser', password='testpassword')
        # Add item to cart
        self.client.get(reverse('add_to_cart', args=[self.product1.id]))
        
        # Check checkout page
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout.html')
        self.assertContains(response, 'Test Phone')
        
        # Submit checkout order form
        post_data = {
            'name': 'Test User',
            'phone': '9876543210',
            'email': 'testuser@example.com',
            'address': '123 Test Lane',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400001'
        }
        response = self.client.post(reverse('checkout'), data=post_data)
        self.assertRedirects(response, reverse('orders'))
        
        # Cart should be empty after checkout
        cart_obj = Cart.objects.get(user=self.user)
        self.assertEqual(cart_obj.items.count(), 0)

        # Verify Order database records
        from .models import Order, OrderItem
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.name, 'Test User')
        self.assertEqual(order.total_price, 10000.00)
        
        # Verify OrderItem database records
        self.assertEqual(OrderItem.objects.count(), 1)
        order_item = OrderItem.objects.first()
        self.assertEqual(order_item.order, order)
        self.assertEqual(order_item.product, self.product1)
        self.assertEqual(order_item.quantity, 1)
        
        # Verify Product stock is decremented
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.quantity, 4)

        # Verify Orders View displays the order history
        response_orders = self.client.get(reverse('orders'))
        self.assertEqual(response_orders.status_code, 200)
        self.assertTemplateUsed(response_orders, 'orders.html')
        self.assertContains(response_orders, f"#PKU-{order.id}")
        self.assertContains(response_orders, "Test Phone")

    def test_user_can_cancel_pending_order_and_restores_stock(self):
        self.client.login(username='testuser', password='testpassword')
        # Create a pending order
        from .models import Order, OrderItem
        order = Order.objects.create(
            user=self.user,
            name='Test User',
            phone='9876543210',
            email='testuser@example.com',
            address='123 Test Lane',
            city='Mumbai',
            state='Maharashtra',
            pincode='400001',
            total_price=10000.00
        )
        OrderItem.objects.create(order=order, product=self.product1, quantity=2, price=10000.00)
        
        # Decrement stock manually to simulate checkout
        self.product1.quantity = 3
        self.product1.save()
        
        response = self.client.get(reverse('cancel_order', args=[order.id]))
        self.assertRedirects(response, reverse('orders'))
        
        # Verify order status updated to Cancelled
        order.refresh_from_db()
        self.assertEqual(order.status, 'Cancelled')
        
        # Verify stock is restored
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.quantity, 5)

    def test_user_cannot_cancel_non_pending_order(self):
        self.client.login(username='testuser', password='testpassword')
        from .models import Order, OrderItem
        order = Order.objects.create(
            user=self.user,
            name='Test User',
            phone='9876543210',
            email='testuser@example.com',
            address='123 Test Lane',
            city='Mumbai',
            state='Maharashtra',
            pincode='400001',
            total_price=10000.00,
            status='Shipped'
        )
        OrderItem.objects.create(order=order, product=self.product1, quantity=1, price=10000.00)
        
        self.product1.quantity = 4
        self.product1.save()
        
        response = self.client.get(reverse('cancel_order', args=[order.id]))
        self.assertRedirects(response, reverse('orders'))
        
        # Verify status did not change and stock was not restored
        order.refresh_from_db()
        self.assertEqual(order.status, 'Shipped')
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.quantity, 4)

    def test_user_cannot_cancel_others_order(self):
        # Create second user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            full_name='Other User',
            password='otherpassword'
        )
        from .models import Order
        order = Order.objects.create(
            user=other_user,
            name='Other User',
            phone='9876543210',
            email='other@example.com',
            address='123 Test Lane',
            city='Mumbai',
            state='Maharashtra',
            pincode='400001',
            total_price=10000.00
        )
        
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('cancel_order', args=[order.id]))
        self.assertRedirects(response, reverse('orders'))
        
        # Status should remain Pending since current user is not the owner
        order.refresh_from_db()
        self.assertEqual(order.status, 'Pending')

    def test_anonymous_user_badge_counts_in_context(self):
        response = self.client.get(reverse('product'))
        self.assertEqual(response.context['cart_count'], 0)
        self.assertEqual(response.context['wishlist_count'], 0)

    def test_authenticated_user_badge_counts_in_context(self):
        self.client.login(username='testuser', password='testpassword')
        # Add to cart
        self.client.get(reverse('add_to_cart', args=[self.product1.id]))
        # Add to wishlist
        self.client.get(reverse('add_to_wishlist', args=[self.product1.id]))
        
        response = self.client.get(reverse('product'))
        self.assertEqual(response.context['cart_count'], 1)
        self.assertEqual(response.context['wishlist_count'], 1)

    def test_cart_delivery_charge_calculation_below_500(self):
        self.client.login(username='testuser', password='testpassword')
        # Create a cheap product (price: ₹150)
        cheap_product = Product.objects.create(
            name='Cheap Socks',
            slug='cheap-socks',
            category=self.category,
            price=150.00,
            quantity=10,
            is_active=True
        )
        # Add to cart
        self.client.get(reverse('add_to_cart', args=[cheap_product.id]))
        
        cart_obj = Cart.objects.get(user=self.user)
        self.assertEqual(cart_obj.get_subtotal(), 150.00)
        self.assertEqual(cart_obj.get_delivery_charge(), 200.00)
        self.assertEqual(cart_obj.get_total_price(), 350.00)

    def test_cart_delivery_charge_calculation_above_500(self):
        self.client.login(username='testuser', password='testpassword')
        # Add a product costing ₹10000
        self.client.get(reverse('add_to_cart', args=[self.product1.id]))
        
        cart_obj = Cart.objects.get(user=self.user)
        self.assertEqual(cart_obj.get_subtotal(), 10000.00)
        self.assertEqual(cart_obj.get_delivery_charge(), 0)
        self.assertEqual(cart_obj.get_total_price(), 10000.00)
