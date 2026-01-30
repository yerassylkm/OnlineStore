"""
Orders: cart, checkout, order creation (MongoDB).
"""
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from core.auth_utils import login_required_mongo, get_current_user
from core.mongodb import (
    cart_items_collection,
    orders_collection,
    order_items_collection,
    product_variants_collection,
    products_collection,
    to_object_id,
)
from bson.objectid import ObjectId
from datetime import datetime


@login_required_mongo
def cart(request):
    """Корзина клиента."""
    user = get_current_user(request)
    uid = user["_id"]
    items = list(cart_items_collection().find({"user_id": uid}))
    total = Decimal("0")
    cart_list = []
    for item in items:
        variant = product_variants_collection().find_one({"_id": item["product_variant_id"]})
        if not variant:
            continue
        product = products_collection().find_one({"_id": variant["product_id"]})
        if not product:
            continue
        price = Decimal(str(product.get("price", 0)))
        qty = item.get("quantity", 1)
        subtotal = price * qty
        total += subtotal
        cart_list.append({
            "id": str(item["_id"]),
            "product_name": product.get("name", ""),
            "sku": product.get("sku", ""),
            "size": variant.get("size", ""),
            "color": variant.get("color", ""),
            "quantity": qty,
            "price": price,
            "subtotal": subtotal,
        })
    return render(request, "orders/cart.html", {"items": cart_list, "total_price": total})


@login_required_mongo
def cart_add(request, variant_id):
    """Добавить в корзину (вариант товара)."""
    user = get_current_user(request)
    uid = user["_id"]
    vid = to_object_id(variant_id)
    if not vid:
        return redirect("store:catalog")
    variant = product_variants_collection().find_one({"_id": vid})
    if not variant or variant.get("quantity", 0) < 1:
        return redirect("store:catalog")
    coll = cart_items_collection()
    existing = coll.find_one({"user_id": uid, "product_variant_id": vid})
    if existing:
        coll.update_one(
            {"_id": existing["_id"]},
            {"$inc": {"quantity": 1}}
        )
    else:
        coll.insert_one({
            "user_id": uid,
            "product_variant_id": vid,
            "quantity": 1,
        })
    next_url = request.POST.get("next") or request.GET.get("next") or "orders:cart"
    return redirect(next_url)


@login_required_mongo
@require_POST
def cart_remove(request, item_id):
    """Удалить позицию из корзины."""
    user = get_current_user(request)
    uid = user["_id"]
    iid = to_object_id(item_id)
    if iid:
        cart_items_collection().delete_one({"_id": iid, "user_id": uid})
    return redirect("orders:cart")


@login_required_mongo
def checkout(request):
    """Оформление заказа: форма ФИО, адрес, время доставки."""
    from .forms import CheckoutForm

    user = get_current_user(request)
    uid = user["_id"]
    items = list(cart_items_collection().find({"user_id": uid}))
    if not items:
        return redirect("orders:cart")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Считаем итог по корзине
            total = Decimal("0")
            order_items_data = []
            for item in items:
                variant = product_variants_collection().find_one({"_id": item["product_variant_id"]})
                if not variant:
                    continue
                product = products_collection().find_one({"_id": variant["product_id"]})
                if not product:
                    continue
                price = Decimal(str(product.get("price", 0)))
                qty = item.get("quantity", 1)
                total += price * qty
                order_items_data.append({
                    "product_name": product.get("name", ""),
                    "sku": product.get("sku", ""),
                    "size": variant.get("size", ""),
                    "color": variant.get("color", ""),
                    "quantity": qty,
                    "price": float(price),
                })
            if not order_items_data:
                return redirect("orders:cart")

            full_name = form.cleaned_data["full_name"]
            address = form.cleaned_data["address"]
            delivery_time = form.cleaned_data.get("delivery_time") or ""

            order_doc = {
                "user_id": uid,
                "full_name": full_name,
                "address": address,
                "delivery_time": delivery_time,
                "status": "new",
                "total_price": float(total),
                "created_at": datetime.utcnow(),
            }
            r = orders_collection().insert_one(order_doc)
            order_id = r.inserted_id

            for oi in order_items_data:
                oi["order_id"] = order_id
                order_items_collection().insert_one(oi)

            # Очистить корзину
            cart_items_collection().delete_many({"user_id": uid})

            # Редирект на страницу оплаты
            return redirect("payment:payment_create", order_id=str(order_id))
    else:
        full_name = f"{user.get('surname', '')} {user.get('name', '')}".strip() or user.get("email", "")
        form = CheckoutForm(initial={"full_name": full_name})

    # Итог корзины для отображения
    total = Decimal("0")
    for item in items:
        variant = product_variants_collection().find_one({"_id": item["product_variant_id"]})
        if variant:
            product = products_collection().find_one({"_id": variant["product_id"]})
            if product:
                total += Decimal(str(product.get("price", 0))) * item.get("quantity", 1)

    return render(request, "orders/checkout.html", {"form": form, "total_price": total})


def _get_cart_for_checkout(user_id):
    """Вспомогательно: список позиций корзины для шаблона."""
    items = list(cart_items_collection().find({"user_id": user_id}))
    result = []
    for item in items:
        variant = product_variants_collection().find_one({"_id": item["product_variant_id"]})
        if not variant:
            continue
        product = products_collection().find_one({"_id": variant["product_id"]})
        if not product:
            continue
        result.append({
            "product_name": product.get("name"),
            "size": variant.get("size"),
            "color": variant.get("color"),
            "quantity": item.get("quantity", 1),
            "price": product.get("price"),
        })
    return result
