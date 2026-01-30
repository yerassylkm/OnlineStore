from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("", views.cart, name="cart"),
    path("add/<str:variant_id>/", views.cart_add, name="cart_add"),
    path("remove/<str:item_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
]
