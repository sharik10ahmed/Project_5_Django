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
