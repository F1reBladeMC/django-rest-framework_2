from django.shortcuts import render
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.db.models import Prefetch

from app.product.serializers import (
    CategorySerializer, TypesSerializer,
    ProductSerializer, ProductCreateSerializer
)
from app.product.models import Category, Types, Product, ProductImage

@method_decorator(cache_page(60 * 15), name='dispatch')  # Кэширование на 15 минут
class CategoryAPIView(ListAPIView):
    serializer_class = CategorySerializer
    
    def get_queryset(self):
        cache_key = 'category_list'
        cached_data = cache.get(cache_key)
        if cached_data is None:
            cached_data = list(Category.objects.all().values('id', 'title', 'image', 'crated_at'))
            cache.set(cache_key, cached_data, 60 * 15)  # 15 минут
        return Category.objects.all()

@method_decorator(cache_page(60 * 10), name='dispatch')  # Кэширование на 10 минут
class TypesAPIView(ListAPIView):
    serializer_class = TypesSerializer
    
    def get_queryset(self):
        return Types.objects.select_related('category').all()

@method_decorator(cache_page(60 * 5), name='dispatch')  # Кэширование на 5 минут
class ProductAPIView(ListAPIView):
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        return Product.objects.select_related(
            'category', 'types_product'
        ).prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.all())
        ).all()
        
    def list(self, request, *args, **kwargs):
        # Дополнительное кэширование для списка продуктов
        cache_key = 'product_list'
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, 60 * 5)  # 5 минут
            return response
        
        return Response(cached_data)


class ProductCreateView(CreateAPIView):
    serializer_class = ProductCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Создаем продукт
        product = serializer.save()
        
        # Очищаем кэш продуктов после создания нового
        cache.delete('product_list')
        
        # Возвращаем созданный продукт с полной информацией
        product_serializer = ProductSerializer(
            product, context={'request': request}
        )
        
        return Response(
            product_serializer.data,
            status=status.HTTP_201_CREATED
        )
