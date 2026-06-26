from django.urls import path
from .views import admin_order_list, customer_create, hello_view, order_create, product_list

urlpatterns = [
    path('', hello_view),
    path('api/products/', product_list),
    path('api/customers/', customer_create),
    path('api/orders/', order_create),
    path('api/admin/orders/', admin_order_list),
]
