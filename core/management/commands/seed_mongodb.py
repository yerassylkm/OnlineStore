"""
Management command: заполнить MongoDB начальными данными (категории, товары, варианты).
Запуск: python manage.py seed_mongodb
"""
from django.core.management.base import BaseCommand
from core.mongodb import (
    get_db,
    categories_collection,
    products_collection,
    product_variants_collection,
)


class Command(BaseCommand):
    help = "Заполнить MongoDB категориями и примерами товаров"

    def handle(self, *args, **options):
        db = get_db()
        cat_coll = categories_collection()
        prod_coll = products_collection()
        var_coll = product_variants_collection()

        # Категории: Мужское, Женское
        if cat_coll.count_documents({}) == 0:
            cat_coll.insert_many([
                {"name": "Мужское", "slug": "muzhskoe"},
                {"name": "Женское", "slug": "zhenskoe"},
            ])
            self.stdout.write("Добавлены категории: Мужское, Женское")

        men = cat_coll.find_one({"slug": "muzhskoe"})
        women = cat_coll.find_one({"slug": "zhenskoe"])
        if not men or not women:
            self.stdout.write(self.style.ERROR("Категории не найдены."))
            return

        # Примеры товаров (если ещё нет)
        if prod_coll.count_documents({}) == 0:
            products_data = [
                {
                    "category_id": men["_id"],
                    "sku": "M-001",
                    "name": "Мужская футболка базовая",
                    "description": "Классическая хлопковая футболка.",
                    "material": "Хлопок 100%",
                    "price": 990.00,
                    "image": "",
                },
                {
                    "category_id": men["_id"],
                    "sku": "M-002",
                    "name": "Мужские джинсы",
                    "description": "Прямой крой, удобные на каждый день.",
                    "material": "Деним",
                    "price": 2990.00,
                    "image": "",
                },
                {
                    "category_id": women["_id"],
                    "sku": "W-001",
                    "name": "Женское платье летнее",
                    "description": "Лёгкое платье для лета.",
                    "material": "Лён",
                    "price": 2490.00,
                    "image": "",
                },
                {
                    "category_id": women["_id"],
                    "sku": "W-002",
                    "name": "Женская блуза",
                    "description": "Блуза офисная.",
                    "material": "Полиэстер",
                    "price": 1890.00,
                    "image": "",
                },
            ]
            prod_coll.insert_many(products_data)
            self.stdout.write("Добавлены примеры товаров.")

        # Варианты (размер, цвет) для каждого товара
        for product in prod_coll.find({}):
            exists = var_coll.find_one({"product_id": product["_id"]})
            if exists:
                continue
            sizes = ["S", "M", "L", "XL"]
            colors = ["Чёрный", "Белый", "Серый"]
            for size in sizes:
                for color in colors:
                    var_coll.insert_one({
                        "product_id": product["_id"],
                        "size": size,
                        "color": color,
                        "quantity": 10,
                    })
            self.stdout.write(f"Варианты добавлены для товара: {product.get('name')}")

        self.stdout.write(self.style.SUCCESS("Готово."))
