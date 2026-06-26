from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import Order, Product
from .serializers import (
    CustomerSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    ProductSerializer,
)

api_overview_response = openapi.Response(
    "API haqida qisqa ma'lumot",
    openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "message": openapi.Schema(type=openapi.TYPE_STRING, title="API nomi", description="API nomi"),
            "endpoints": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                title="Endpointlar",
                description="Asosiy endpointlar",
            ),
        },
    ),
    examples={
        "application/json": {
            "message": "AZIM Marinade API",
            "endpoints": {
                "products": "/api/products/",
                "customers": "/api/customers/",
                "orders": "/api/orders/",
                "admin_orders": "/api/admin/orders/",
            },
        }
    },
)

validation_error_response = openapi.Response(
    "Validatsiya xatosi",
    openapi.Schema(
        type=openapi.TYPE_OBJECT,
        additional_properties=openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
    ),
    examples={
        "application/json": {
            "phone": ["Telefon raqam +998901234567 formatida bo'lishi kerak."],
            "items": ["Kamida bitta mahsulot tanlang."],
        }
    },
)


@swagger_auto_schema(
    method="get",
    operation_summary="API ma'lumotlari",
    operation_description="AZIM Marinade API endpointlari haqida qisqa ma'lumot qaytaradi.",
    tags=["Umumiy"],
    responses={200: api_overview_response},
)
@api_view(['GET'])
@permission_classes([AllowAny])
def hello_view(request):
    return Response(
        {
            "message": "AZIM Marinade API",
            "endpoints": {
                "products": "/api/products/",
                "customers": "/api/customers/",
                "orders": "/api/orders/",
                "admin_orders": "/api/admin/orders/",
            },
        }
    )


@swagger_auto_schema(
    method="get",
    operation_summary="Mahsulotlar ro'yxati",
    operation_description=(
        "Saytdagi aktiv AZIM Marinade mahsulotlarini narxi, og'irligi va rasm yo'li bilan qaytaradi. "
        "Frontend savatga qo'shishda shu endpointdagi `id` qiymatini buyurtma ichida `product_id` qilib yuboradi."
    ),
    operation_id="products_list",
    tags=["Mahsulotlar"],
    responses={200: ProductSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([AllowAny])
def product_list(request):
    products = Product.objects.filter(is_active=True)
    return Response(ProductSerializer(products, many=True).data)


@swagger_auto_schema(
    method="post",
    operation_summary="Mijoz qo'shish",
    operation_description=(
        "Yangi mijoz ma'lumotlarini yaratadi. Telefon raqam +998 formatida bo'lishi kerak. "
        "Buyurtma endpointi mijozni avtomatik yaratgani uchun frontendda bu endpoint alohida ishlatilishi shart emas."
    ),
    operation_id="customers_create",
    tags=["Mijozlar"],
    request_body=CustomerSerializer,
    responses={201: CustomerSerializer, 400: validation_error_response},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def customer_create(request):
    serializer = CustomerSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    customer = serializer.save()
    return Response(CustomerSerializer(customer).data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method="post",
    operation_summary="Buyurtma berish",
    operation_description=(
        "Mijoz, manzil va mahsulotlar ro'yxati bo'yicha buyurtma yaratadi. "
        "Jami summa server tomonda mahsulot narxlaridan hisoblanadi va buyurtma Telegram adminlarga yuboriladi. "
        "`items` ichida `product_id` va `quantity` yuborish kifoya."
    ),
    operation_id="orders_create",
    tags=["Buyurtmalar"],
    request_body=OrderCreateSerializer,
    responses={201: OrderSerializer, 400: validation_error_response},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def order_create(request):
    serializer = OrderCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order = serializer.save()
    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method="get",
    operation_summary="Admin buyurtmalar ro'yxati",
    operation_description="Barcha buyurtmalarni mijoz va mahsulotlari bilan qaytaradi. Faqat admin token bilan ishlaydi.",
    operation_id="admin_orders_list",
    tags=["Admin"],
    responses={200: OrderSerializer(many=True), 401: "Token kerak", 403: "Admin huquqi kerak"},
)
@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_order_list(request):
    orders = Order.objects.select_related("customer").prefetch_related("items", "items__product")
    return Response(OrderSerializer(orders, many=True).data)
