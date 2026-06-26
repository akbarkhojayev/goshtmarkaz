from django.db import models
from django.utils import timezone


class Product(models.Model):
    name = models.CharField(max_length=180, unique=True)
    description = models.TextField(blank=True)
    price = models.PositiveIntegerField()
    weight = models.CharField(max_length=50, default="1 kg")
    image = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("sort_order", "name")

    def __str__(self):
        return self.name


class Customer(models.Model):
    full_name = models.CharField(max_length=180)
    phone = models.CharField(max_length=30, db_index=True)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.full_name} ({self.phone})"


class TelegramAdmin(models.Model):
    name = models.CharField(max_length=120, default="Admin")
    chat_id = models.CharField(max_length=80, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Telegram admin"
        verbose_name_plural = "Telegram adminlar"

    def __str__(self):
        status = "aktiv" if self.is_active else "o'chirilgan"
        return f"{self.name} ({self.chat_id}) - {status}"


class Order(models.Model):
    PAYMENT_CASH = "naqd"
    PAYMENT_CARD = "karta"
    PAYMENT_CLICK = "click"

    PAYMENT_CHOICES = (
        (PAYMENT_CASH, "Naqd pul"),
        (PAYMENT_CARD, "Bank kartasi"),
        (PAYMENT_CLICK, "Click / Payme"),
    )

    STATUS_NEW = "new"
    STATUS_ACCEPTED = "accepted"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = (
        (STATUS_NEW, "Yangi"),
        (STATUS_ACCEPTED, "Qabul qilindi"),
        (STATUS_DELIVERED, "Yetkazildi"),
        (STATUS_CANCELED, "Bekor qilindi"),
    )

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders")
    address = models.CharField(max_length=255)
    note = models.TextField(blank=True)
    payment = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default=PAYMENT_CASH)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    total_price = models.PositiveIntegerField(default=0)
    telegram_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Buyurtma #{self.pk} - {self.customer.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    product_name = models.CharField(max_length=180)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.PositiveIntegerField()
    line_total = models.PositiveIntegerField()

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
