"""
Payment: redirect to gateway (Stripe/CloudPayments), result page.
"""
import os
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST
from core.auth_utils import login_required_mongo, get_current_user
from core.mongodb import orders_collection, payments_collection, to_object_id


@login_required_mongo
def payment_create(request, order_id):
    """Страница оплаты: перенаправление на шлюз (Stripe/CloudPayments)."""
    uid = get_current_user(request)["_id"]
    oid = to_object_id(order_id)
    if not oid:
        return redirect("profile")
    order = orders_collection().find_one({"_id": oid, "user_id": uid})
    if not order:
        return redirect("profile")

    total_cents = int(float(order.get("total_price", 0)) * 100)
    payment_system = os.environ.get("PAYMENT_SYSTEM", "stripe").lower()

    if payment_system == "stripe":
        return _stripe_checkout(request, order, total_cents)
    return _cloudpayments_checkout(request, order, total_cents)


def _stripe_checkout(request, order, total_cents):
    """Stripe: создаём сессию и редирект на Stripe Checkout."""
    try:
        import stripe
        stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
        if not stripe.api_key:
            return _mock_payment_success(request, order, "Stripe (ключ не задан)")
        success_url = request.build_absolute_uri(f"/payment/result/?order_id={str(order['_id'])}&status=success")
        cancel_url = request.build_absolute_uri("/payment/result/?status=cancel")
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "rub",
                    "product_data": {"name": f"Заказ #{str(order['_id'])[:8]}"},
                    "unit_amount": total_cents,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"order_id": str(order["_id"])},
        )
        return redirect(session.url)
    except Exception:
        return _mock_payment_success(request, order, "Stripe (ошибка)")


def _cloudpayments_checkout(request, order, total_cents):
    """CloudPayments: форма с виджетом или редирект. Упрощённо — мок."""
    return _mock_payment_success(request, order, "CloudPayments (демо)")


def _mock_payment_success(request, order, system):
    """Демо: сразу помечаем заказ оплаченным и создаём запись Payments."""
    payments_collection().insert_one({
        "order_id": order["_id"],
        "payment_system": system,
        "payment_status": "оплачено",
        "transaction_id": f"mock-{order['_id']}",
        "created_at": __import__("datetime").datetime.utcnow(),
    })
    orders_collection().update_one(
        {"_id": order["_id"]},
        {"$set": {"status": "paid"}}
    )
    return redirect(f"/payment/result/?order_id={order['_id']}&status=success")


@require_GET
def payment_result(request):
    """Результат оплаты: возврат на сайт, статус заказа и оплаты."""
    order_id = request.GET.get("order_id")
    status = request.GET.get("status", "")
    order = None
    payment = None
    if order_id:
        oid = to_object_id(order_id)
        if oid:
            order = orders_collection().find_one({"_id": oid})
            if order:
                order["id"] = str(order["_id"])
                order["created_at_str"] = order.get("created_at").strftime("%d.%m.%Y %H:%M") if order.get("created_at") else ""
            payment = payments_collection().find_one({"order_id": oid}) if oid else None
            if payment:
                payment["id"] = str(payment.get("_id", ""))

    return render(request, "orders/payment_result.html", {
        "order": order,
        "payment": payment,
        "success": status == "success",
    })
