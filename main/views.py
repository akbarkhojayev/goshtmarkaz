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


@api_view(["GET"])
@permission_classes([AllowAny])
def product_list(request):
    products = Product.objects.filter(is_active=True)
    return Response(ProductSerializer(products, many=True).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def customer_create(request):
    serializer = CustomerSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    customer = serializer.save()
    return Response(CustomerSerializer(customer).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def order_create(request):
    serializer = OrderCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order = serializer.save()
    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_order_list(request):
    orders = Order.objects.select_related("customer").prefetch_related("items", "items__product")
    return Response(OrderSerializer(orders, many=True).data)
