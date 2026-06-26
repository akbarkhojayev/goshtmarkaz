from django.contrib import admin

from .models import Customer, Order, OrderItem, Product, TelegramAdmin


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "weight", "is_active", "sort_order")
    list_editable = ("price", "is_active", "sort_order")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "address", "created_at")
    search_fields = ("full_name", "phone", "address")
    readonly_fields = ("created_at",)


@admin.register(TelegramAdmin)
class TelegramAdminAdmin(admin.ModelAdmin):
    list_display = ("name", "chat_id", "is_active", "created_at")
    list_editable = ("is_active",)
    search_fields = ("name", "chat_id")
    list_filter = ("is_active",)
    readonly_fields = ("created_at",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "quantity", "unit_price", "line_total")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "address",
        "payment",
        "status",
        "total_price",
        "telegram_sent",
        "created_at",
    )
    list_filter = ("status", "payment", "telegram_sent", "created_at")
    search_fields = ("customer__full_name", "customer__phone", "address")
    readonly_fields = ("customer", "address", "note", "payment", "total_price", "telegram_sent", "created_at")
    inlines = (OrderItemInline,)
