import re

from django.db import transaction
from rest_framework import serializers

from .models import Customer, Order, OrderItem, Product
from .telegram import notify_order_created


PHONE_PATTERN = re.compile(r"^\+?998\d{9}$")


def normalize_phone(value):
    return re.sub(r"[\s()-]", "", value or "")


def validate_uz_phone(value):
    phone = normalize_phone(value)
    if not PHONE_PATTERN.match(phone):
        raise serializers.ValidationError("Telefon raqam +998901234567 formatida bo'lishi kerak.")
    return phone


class ProductSerializer(serializers.ModelSerializer):
    price_display = serializers.SerializerMethodField(label="Narx ko'rinishi")

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "price",
            "price_display",
            "weight",
            "image",
        )
        extra_kwargs = {
            "id": {"label": "Mahsulot ID"},
            "name": {"label": "Mahsulot nomi"},
            "description": {"label": "Tavsif"},
            "price": {"label": "Narx", "help_text": "Narx so'mda, masalan: 139900"},
            "weight": {"label": "Og'irlik"},
            "image": {"label": "Rasm yo'li"},
        }
        swagger_schema_fields = {
            "example": {
                "id": 2,
                "name": "Dandana Steak",
                "description": "AZIM Marinade go'sht markazi mahsuloti",
                "price": 139900,
                "price_display": "139 900 so'm",
                "weight": "1 kg",
                "image": "/images/dandana steak.jpg",
            }
        }

    def get_price_display(self, obj):
        return f"{obj.price:,}".replace(",", " ") + " so'm"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ("id", "full_name", "phone", "address", "created_at")
        read_only_fields = ("id", "created_at")
        extra_kwargs = {
            "id": {"label": "Mijoz ID"},
            "full_name": {"label": "Ism familiya"},
            "phone": {
                "label": "Telefon raqam",
                "help_text": "Masalan: +998901234567. Probel, qavs va tire avtomatik tozalanadi.",
            },
            "address": {"label": "Manzil"},
            "created_at": {"label": "Yaratilgan vaqti"},
        }
        swagger_schema_fields = {
            "example": {
                "full_name": "Ali Valiyev",
                "phone": "+998901234567",
                "address": "Rishton, Farg'ona",
            }
        }

    def validate_full_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Ism familiya kamida 3 ta belgidan iborat bo'lishi kerak.")
        return value

    def validate_phone(self, value):
        return validate_uz_phone(value)

    def validate_address(self, value):
        return value.strip()


class OrderItemCreateSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        required=False,
        label="Mahsulot ID",
        help_text="Mahsulot ID sini yuboring. product_id ham qabul qilinadi.",
    )
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source="product",
        write_only=True,
        required=False,
        label="Mahsulot ID",
    )
    quantity = serializers.IntegerField(
        min_value=1,
        max_value=100,
        label="Miqdor",
        help_text="Nechta kg buyurtma qilinadi. Masalan: 2.",
    )

    def validate(self, attrs):
        if "product" not in attrs:
            raise serializers.ValidationError({"product": "Mahsulot tanlang."})
        return attrs


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True, label="Mahsulot ID")

    class Meta:
        model = OrderItem
        fields = ("product_id", "product_name", "quantity", "unit_price", "line_total")
        extra_kwargs = {
            "product_name": {"label": "Mahsulot nomi"},
            "quantity": {"label": "Miqdor"},
            "unit_price": {"label": "Birlik narxi"},
            "line_total": {"label": "Qator jami"},
        }
        swagger_schema_fields = {
            "example": {
                "product_id": 2,
                "product_name": "Dandana Steak",
                "quantity": 2,
                "unit_price": 139900,
                "line_total": 279800,
            }
        }


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    payment_label = serializers.CharField(source="get_payment_display", read_only=True, label="To'lov nomi")
    status_label = serializers.CharField(source="get_status_display", read_only=True, label="Status nomi")

    class Meta:
        model = Order
        fields = (
            "id",
            "customer",
            "address",
            "note",
            "payment",
            "payment_label",
            "status",
            "status_label",
            "total_price",
            "telegram_sent",
            "created_at",
            "items",
        )
        extra_kwargs = {
            "id": {"label": "Buyurtma ID"},
            "address": {"label": "Yetkazib berish manzili"},
            "note": {"label": "Izoh"},
            "payment": {"label": "To'lov turi"},
            "status": {"label": "Buyurtma statusi"},
            "total_price": {"label": "Jami summa"},
            "telegram_sent": {"label": "Telegramga yuborildi"},
            "created_at": {"label": "Yaratilgan vaqti"},
        }
        swagger_schema_fields = {
            "example": {
                "id": 1,
                "customer": {
                    "id": 1,
                    "full_name": "Ali Valiyev",
                    "phone": "+998901234567",
                    "address": "Rishton, Farg'ona",
                    "created_at": "2026-06-27T10:00:00Z",
                },
                "address": "Rishton, Farg'ona",
                "note": "Kechqurun yetkazilsin",
                "payment": "naqd",
                "payment_label": "Naqd pul",
                "status": "new",
                "status_label": "Yangi",
                "total_price": 279800,
                "telegram_sent": True,
                "created_at": "2026-06-27T10:00:00Z",
                "items": [
                    {
                        "product_id": 2,
                        "product_name": "Dandana Steak",
                        "quantity": 2,
                        "unit_price": 139900,
                        "line_total": 279800,
                    }
                ],
            }
        }


class OrderCreateSerializer(serializers.Serializer):
    full_name = serializers.CharField(
        max_length=180,
        required=False,
        label="Ism familiya",
    )
    name = serializers.CharField(
        max_length=180,
        required=False,
        write_only=True,
        label="Ism familiya",
        help_text="full_name o'rniga name ham yuborish mumkin.",
    )
    phone = serializers.CharField(
        max_length=30,
        label="Telefon raqam",
        help_text="Masalan: +998901234567. Probel, qavs va tire avtomatik tozalanadi.",
    )
    address = serializers.CharField(max_length=255, label="Yetkazib berish manzili")
    note = serializers.CharField(required=False, allow_blank=True, label="Izoh")
    payment = serializers.ChoiceField(
        choices=Order.PAYMENT_CHOICES,
        default=Order.PAYMENT_CASH,
        label="To'lov turi",
        help_text="Variantlar: naqd, karta, click",
    )
    items = OrderItemCreateSerializer(many=True, label="Mahsulotlar")

    class Meta:
        swagger_schema_fields = {
            "example": {
                "full_name": "Ali Valiyev",
                "phone": "+998901234567",
                "address": "Rishton, Farg'ona, Markaz",
                "note": "Kechqurun yetkazilsin",
                "payment": "naqd",
                "items": [
                    {"product_id": 2, "quantity": 2},
                    {"product_id": 5, "quantity": 1},
                ],
            }
        }

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Kamida bitta mahsulot tanlang.")
        return items

    def validate(self, attrs):
        full_name = (attrs.get("full_name") or attrs.pop("name", "")).strip()
        if not full_name:
            raise serializers.ValidationError({"full_name": "Ism familiya kiriting."})
        if len(full_name) < 3:
            raise serializers.ValidationError({"full_name": "Ism familiya kamida 3 ta belgidan iborat bo'lishi kerak."})
        attrs["full_name"] = full_name
        try:
            attrs["phone"] = validate_uz_phone(attrs["phone"])
        except serializers.ValidationError as exc:
            raise serializers.ValidationError({"phone": exc.detail})
        attrs["address"] = attrs["address"].strip()
        attrs["note"] = attrs.get("note", "").strip()
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        full_name = validated_data.pop("full_name")
        phone = validated_data.pop("phone")
        address = validated_data["address"]

        customer, _ = Customer.objects.update_or_create(
            phone=phone,
            defaults={"full_name": full_name, "address": address},
        )
        order = Order.objects.create(customer=customer, **validated_data)

        total = 0
        for item in items_data:
            product = item["product"]
            quantity = item["quantity"]
            line_total = product.price * quantity
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                quantity=quantity,
                unit_price=product.price,
                line_total=line_total,
            )
            total += line_total

        order.total_price = total
        order.telegram_sent = notify_order_created(order)
        order.save(update_fields=("total_price", "telegram_sent"))
        return order
