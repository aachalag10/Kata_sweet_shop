from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Sweet, Order
from django.urls import reverse

class SweetModelTest(TestCase):
    def test_create_sweet(self):
        sweet = Sweet.objects.create(name="Ladoo", description="Delicious", price=20.00, quantity_available=10)
        self.assertEqual(sweet.name, "Ladoo")
        self.assertEqual(sweet.quantity_available, 10)

class OrderPlacementTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='sweetuser', password='testpass')
        self.client.login(username='sweetuser', password='testpass')
        self.sweet = Sweet.objects.create(name="Barfi", description="Milky barfi", price=25.00, quantity_available=5)

    def test_order_reduces_quantity(self):
        response = self.client.post(reverse('place_order', args=[self.sweet.id]), {'quantity': 2})
        self.sweet.refresh_from_db()
        self.assertEqual(self.sweet.quantity_available, 3)
        self.assertEqual(Order.objects.count(), 1)

    def test_cannot_order_more_than_available(self):
        response = self.client.post(reverse('place_order', args=[self.sweet.id]), {'quantity': 10}, follow=True)
        self.sweet.refresh_from_db()
        self.assertEqual(self.sweet.quantity_available, 5)  # Should remain unchanged
        self.assertEqual(Order.objects.count(), 0)
        self.assertContains(response, "Only 5 Barfi(s) available!")

    def test_login_required_for_order(self):
        self.client.logout()
        response = self.client.post(reverse('place_order', args=[self.sweet.id]), {'quantity': 1})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_login_required_for_view_orders(self):
        self.client.logout()
        response = self.client.get(reverse('view_orders'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_create_multiple_orders(self):
        Order.objects.create(user=self.user, sweet=self.sweet, quantity=2)
        Order.objects.create(user=self.user, sweet=self.sweet, quantity=1)
        self.assertEqual(Order.objects.count(), 2)

    def test_sweet_quantity_does_not_go_negative(self):
        response = self.client.post(reverse('place_order', args=[self.sweet.id]), {'quantity': 10}, follow=True)
        self.sweet.refresh_from_db()
        self.assertGreaterEqual(self.sweet.quantity_available, 0)

    def test_view_orders_content(self):
        Order.objects.create(user=self.user, sweet=self.sweet, quantity=1)
        response = self.client.get(reverse('view_orders'))
        self.assertContains(response, "Barfi")

class SweetShopTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='sweetuser', password='testpass123')
        self.client.login(username='sweetuser', password='testpass123')

        self.sweet = Sweet.objects.create(
            name="Kaju Katli",
            description="Rich and delicious",
            price=150.0,
            quantity_available=10
        )

    def test_sweet_created(self):
        self.assertEqual(self.sweet.name, "Kaju Katli")
        self.assertEqual(self.sweet.quantity_available, 10)

    def test_homepage_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kaju Katli")

    def test_place_order_success(self):
        response = self.client.post(
            reverse('place_order', args=[self.sweet.id]),
            {'quantity': 2},
            follow=True
        )
        self.assertEqual(Order.objects.count(), 1)
        self.assertContains(response, "Order placed for 2 Kaju Katli(s)!")
        self.sweet.refresh_from_db()
        self.assertEqual(self.sweet.quantity_available, 8)

    def test_view_orders_page(self):
        Order.objects.create(user=self.user, sweet=self.sweet, quantity=1)
        response = self.client.get(reverse('view_orders'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sweetuser ordered 1 × Kaju Katli")

    def test_homepage_no_sweets(self):
        Sweet.objects.all().delete()
        response = self.client.get(reverse('home'))
        self.assertContains(response, "No sweets available.")

    def test_create_multiple_sweets(self):
        Sweet.objects.create(name="Rasgulla", description="Spongy", price=40.00, quantity_available=8)
        self.assertEqual(Sweet.objects.count(), 2)
