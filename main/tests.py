from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .models import Customer, Order, Product, TelegramAdmin
from .telegram import get_admin_chat_ids


@override_settings(TELEGRAM_BOT_TOKEN="", TELEGRAM_ADMIN_CHAT_ID="")
class OrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.product = Product.objects.get(name="Dandana Steak")

    def test_product_list(self):
        response = self.client.get("/api/products/")

        self.assertEqual(response.status_code, 200)
        names = [product["name"] for product in response.data]
        self.assertIn("Dandana Steak", names)
        dandana = next(product for product in response.data if product["name"] == "Dandana Steak")
        self.assertEqual(dandana["price_display"], "139 900 so'm")

    def test_create_order(self):
        response = self.client.post(
            "/api/orders/",
            {
                "full_name": "Azim Akhmadaliyev",
                "phone": "+998507286965",
                "address": "Rishton, Farg'ona",
                "note": "Kechqurun yetkazilsin",
                "payment": "naqd",
                "items": [{"product": self.product.id, "quantity": 2}],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["total_price"], 279800)
        self.assertFalse(response.data["telegram_sent"])
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.first().items.count(), 1)

    @override_settings(TELEGRAM_ADMIN_CHAT_ID="fallback-chat")
    def test_admin_panel_chat_ids_are_used_before_env_fallback(self):
        TelegramAdmin.objects.create(name="Asosiy admin", chat_id="12345", is_active=True)
        TelegramAdmin.objects.create(name="O'chirilgan admin", chat_id="67890", is_active=False)

        self.assertEqual(get_admin_chat_ids(), ["12345"])
