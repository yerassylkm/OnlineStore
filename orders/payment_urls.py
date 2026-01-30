from django.urls import path
from . import payment_views

urlpatterns = [
    path("create/<str:order_id>/", payment_views.payment_create, name="payment_create"),
    path("result/", payment_views.payment_result, name="payment_result"),
]
