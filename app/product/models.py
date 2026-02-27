from django.db import models
import uuid

class Category(models.Model):
    title = models.CharField(
        max_length=155,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to="category",
        verbose_name='ФОто'
    )
    crated_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категори'
        verbose_name_plural = 'Категорий'

class Types(models.Model):
    title = models.CharField(
        max_length=155,
        verbose_name='Название'
    )
    description = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name='category_type'
    )
    crated_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Тип"
        verbose_name_plural = "Типы"


class Product(models.Model):
    title = models.CharField(
        max_length=155
    )
    description = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name='category_product'
    )
    types_product = models.ForeignKey(
        Types, on_delete=models.CASCADE,
        related_name='type_category'
    )
    price = models.CharField(
        max_length=30
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    is_active = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(
        upload_to='product'
    )

    class Meta:
        verbose_name = 'Фото продукта'
        verbose_name_plural = 'Фото продукта'