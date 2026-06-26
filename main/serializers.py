from django.db import transaction
from rest_framework import serializers

from .models import Customer, Order, OrderItem, Product
from .telegram import notify_order_created


class ProductSerializer(serializers.ModelSerializer):
    price_display = serializers.SerializerMethodField()

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

    def get_price_display(self, obj):
        return f"{obj.price:,}".replace(",", " ") + " so'm"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ("id", "full_name", "phone", "address", "created_at")
        read_only_fields = ("id", "created_at")


class OrderItemCreateSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        required=False,
    )
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source="product",
        write_only=True,
        required=False,
    )
    quantity = serializers.IntegerField(min_value=1, max_value=100)

    def validate(self, attrs):
        if "product" not in attrs:
            raise serializers.ValidationError({"product": "Mahsulot tanlang."})
        return attrs


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)

    class Meta:
        model = OrderItem
        fields = ("product_id", "product_name", "quantity", "unit_price", "line_total")


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    payment_label = serializers.CharField(source="get_payment_display", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

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


class OrderCreateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=180, required=False)
    name = serializers.CharField(max_length=180, required=False, write_only=True)
    phone = serializers.CharField(max_length=30)
    address = serializers.CharField(max_length=255)
    note = serializers.CharField(required=False, allow_blank=True)
    payment = serializers.ChoiceField(choices=Order.PAYMENT_CHOICES, default=Order.PAYMENT_CASH)
    items = OrderItemCreateSerializer(many=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Kamida bitta mahsulot tanlang.")
        return items

    def validate(self, attrs):
        full_name = attrs.get("full_name") or attrs.pop("name", "")
        if not full_name:
            raise serializers.ValidationError({"full_name": "Ism familiya kiriting."})
        attrs["full_name"] = full_name
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        full_name = validated_data.pop("full_name").strip()
        phone = validated_data.pop("phone").strip()
        address = validated_data["address"].strip()

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
