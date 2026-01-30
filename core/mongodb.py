"""
MongoDB Atlas connection and collections for OnlineShop.
All collections follow the project schema.
"""
import os
from pymongo import MongoClient
from bson.objectid import ObjectId

# Берём из Django settings (настраивается в core.settings)
def _get_settings():
    try:
        from django.conf import settings
        return getattr(settings, "MONGODB_URI", None), getattr(settings, "MONGODB_DB_NAME", "onlineshop")
    except Exception:
        return os.environ.get("MONGODB_URI", "mongodb://localhost:27017/"), os.environ.get("MONGODB_DB_NAME", "onlineshop")

MONGODB_URI, DB_NAME = _get_settings()
if MONGODB_URI is None:
    MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")

_client = None


def get_client():
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI)
    return _client


def get_db():
    return get_client()[DB_NAME]


# Collections (schema as per project spec)
def users_collection():
    return get_db()["users"]


def categories_collection():
    return get_db()["categories"]


def products_collection():
    return get_db()["products"]


def product_variants_collection():
    return get_db()["product_variants"]


def cart_items_collection():
    return get_db()["cart_items"]


def orders_collection():
    return get_db()["orders"]


def order_items_collection():
    return get_db()["order_items"]


def payments_collection():
    return get_db()["payments"]


def to_object_id(s):
    """Convert string to ObjectId, return None if invalid."""
    if s is None:
        return None
    try:
        return ObjectId(s)
    except Exception:
        return None
