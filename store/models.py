from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="URL slug")

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True, verbose_name="Артикул")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True)

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    SIZE_CHOICES = [('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL')]

    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    size = models.CharField(max_length=5, choices=SIZE_CHOICES)
    color = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'size', 'color')

    def __str__(self):
        return f"{self.product.name} - {self.size}/{self.color}"