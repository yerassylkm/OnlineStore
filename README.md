# Онлайн магазин одежды

Django-проект с каталогом (мужское/женское), корзиной, оформлением заказа и оплатой (Stripe/CloudPayments). База данных — **MongoDB Atlas**.

## Требования

- Python 3.10+
- MongoDB (локально или MongoDB Atlas)

## Установка

```bash
pip install -r requirements.txt
```

## Настройка MongoDB Atlas

1. Создайте кластер на [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. Получите строку подключения (Connection String).
3. Задайте переменные окружения:

```bash
# Обязательно для Atlas (подставьте свои данные)
set MONGODB_URI=mongodb+srv://USER:PASSWORD@cluster.xxxxx.mongodb.net/
set MONGODB_DB_NAME=onlineshop

# Опционально: для реальной оплаты Stripe
set STRIPE_SECRET_KEY=sk_test_...
set PAYMENT_SYSTEM=stripe
```

Для локального MongoDB:

```bash
set MONGODB_URI=mongodb://localhost:27017/
set MONGODB_DB_NAME=onlineshop
```

## Заполнение БД (категории и примеры товаров)

```bash
python manage.py seed_mongodb
```

## Запуск

```bash
python manage.py runserver
```

- Главная: http://127.0.0.1:8000/
- Каталог: http://127.0.0.1:8000/catalog/
- Корзина: http://127.0.0.1:8000/cart/
- Регистрация/вход: http://127.0.0.1:8000/users/register/ и /users/login/
- Личный кабинет: http://127.0.0.1:8000/profile/ (после входа)

## Страницы и маршруты

| Страница           | URL                    |
|--------------------|------------------------|
| Главная            | `/`                    |
| Каталог            | `/catalog/`            |
| Каталог по категории| `/catalog/muzhskoe/`, `/catalog/zhenskoe/` |
| Карточка товара    | `/catalog/product/<sku>/` |
| Корзина            | `/cart/`               |
| Оформление заказа  | `/cart/checkout/`      |
| Оплата             | `/payment/create/<order_id>/` |
| Результат оплаты   | `/payment/result/`    |
| Личный кабинет     | `/profile/`            |

## База данных (MongoDB)

Коллекции: `users`, `categories`, `products`, `product_variants`, `cart_items`, `orders`, `order_items`, `payments`. Схема соответствует описанию в ТЗ.

## Оплата

- По умолчанию используется демо-режим (заказ сразу помечается как оплаченный).
- Для Stripe задайте `STRIPE_SECRET_KEY` и `PAYMENT_SYSTEM=stripe` — будет редирект на Stripe Checkout.
- Для CloudPayments можно добавить интеграцию в `orders/payment_views.py`.
