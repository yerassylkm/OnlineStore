"""
Store views: main, catalog, product detail (MongoDB).
"""
from django.shortcuts import render, redirect, get_object_or_404
from core.mongodb import (
    categories_collection,
    products_collection,
    product_variants_collection,
    to_object_id,
)


def main(request):
    """Главная страница."""
    categories = list(categories_collection().find())
    for c in categories:
        c["id"] = str(c["_id"])
    # Показать несколько товаров на главной
    products = list(products_collection().find().limit(8))
    for p in products:
        p["id"] = str(p["_id"])
        if p.get("image"):
            p["image_url"] = p["image"] if p["image"].startswith("http") else f"/media/{p['image']}"
        else:
            p["image_url"] = None
    return render(request, "store/main.html", {"categories": categories, "products": products})


def catalog(request, category_slug=None):
    """Каталог: весь каталог или по категории (Мужское/Женское)."""
    categories = list(categories_collection().find())
    for c in categories:
        c["id"] = str(c["_id"])

    query = {}
    category = None
    if category_slug:
        category = next((c for c in categories if c.get("slug") == category_slug), None)
        if category:
            query["category_id"] = category["_id"]

    products = list(products_collection().find(query))
    for p in products:
        p["id"] = str(p["_id"])
        if p.get("image"):
            p["image_url"] = p["image"] if str(p["image"]).startswith("http") else f"/media/{p['image']}"
        else:
            p["image_url"] = None

    return render(request, "store/product/list.html", {
        "category": category,
        "categories": categories,
        "products": products,
    })


def product_detail(request, slug):
    """Страница товара: описание, размер, цвет, материал, фото. slug = sku."""
    product = products_collection().find_one({"sku": slug})
    if not product:
        return redirect("store:catalog")

    product["id"] = str(product["_id"])
    if product.get("image"):
        product["image_url"] = product["image"] if str(product["image"]).startswith("http") else f"/media/{product['image']}"
    else:
        product["image_url"] = None

    variants = list(product_variants_collection().find({"product_id": product["_id"]}))
    for v in variants:
        v["id"] = str(v["_id"])
    product["variants"] = variants

    return render(request, "store/product/detail.html", {"product": product})
