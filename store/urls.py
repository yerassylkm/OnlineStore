from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.main, name="main"),
    path("catalog/", views.catalog, name="catalog"),
    path("catalog/<slug:category_slug>/", views.catalog, name="catalog_by_category"),
    path("catalog/product/<slug:slug>/", views.product_detail, name="product_detail"),
]
