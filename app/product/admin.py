from django.contrib import admin

from app.product.models import Category, Types, Product, ProductImage

admin.site.register(Category)
admin.site.register(Types)
admin.site.register(ProductImage)
admin.site.register(Product)