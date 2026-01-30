"""
Auth views: register and login using MongoDB (session-based).
"""
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from .forms import RegisterForm, LoginForm
from core.mongodb import users_collection


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user_id = form.save_mongo()
            request.session["user_id"] = user_id
            request.session.set_expiry(60 * 60 * 24 * 7)  # 7 days
            next_url = request.GET.get("next") or "store:main"
            return redirect(next_url)
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = users_collection().find_one({"email": email})
            if user and check_password(password, user.get("password", "")):
                request.session["user_id"] = str(user["_id"])
                request.session.set_expiry(60 * 60 * 24 * 7)
                next_url = request.GET.get("next") or "store:main"
                return redirect(next_url)
            form.add_error(None, "Неверный email или пароль.")
    else:
        form = LoginForm()
    return render(request, "registration/login.html", {"form": form})


def logout_view(request):
    request.session.flush()
    return redirect("store:main")


def profile_view(request):
    """Личный кабинет: история заказов и их статус."""
    from core.auth_utils import login_required_mongo, get_current_user
    from core.mongodb import orders_collection, order_items_collection, payments_collection

    user = get_current_user(request)
    if not user:
        return redirect("users:login")

    uid = user["_id"]
    orders_cursor = orders_collection().find({"user_id": uid}).sort("created_at", -1)
    orders = []
    for o in orders_cursor:
        o["id"] = str(o["_id"])
        o["created_at_str"] = o.get("created_at").strftime("%d.%m.%Y %H:%M") if o.get("created_at") else ""
        items = list(order_items_collection().find({"order_id": o["_id"]}))
        o["items"] = items
        pay = payments_collection().find_one({"order_id": o["_id"]})
        o["payment_status"] = pay.get("payment_status", "—") if pay else "—"
        orders.append(o)

    return render(request, "profile/orders.html", {"orders": orders})
