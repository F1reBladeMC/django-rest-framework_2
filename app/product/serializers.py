from rest_framework import serializers
from django.core.exceptions import ValidationError

from app.product.models import Category, Types, ProductImage, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'image', 'crated_at']
        
    def validate_title(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Название категории должно содержать минимум 2 символа")
        return value.strip()

class TypesSerializer(serializers.ModelSerializer):
    category_title = serializers.CharField(source='category.title', read_only=True)
    
    class Meta:
        model = Types
        fields = ['id', 'title', 'description', 'category', 'category_title', 'crated_at']
        
    def validate_title(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Название типа должно содержать минимум 2 символа")
        return value.strip()
        
    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Описание должно содержать минимум 10 символов")
        return value.strip()

class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'product']
        
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            url = obj.image.url
            return request.build_absolute_uri(url) if request else url
        return None

class ProductSerializer(serializers.ModelSerializer):
    first_image = serializers.SerializerMethodField()
    category_title = serializers.CharField(source='category.title', read_only=True)
    types_title = serializers.CharField(source='types_product.title', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'uuid', 'title', 'description',
            'category', 'category_title', 'types_product', 'types_title', 
            'created_at', 'price', 'first_image', 'images', 'is_active'
        ]

    def get_first_image(self, obj):
        first_img = obj.images.first()
        if first_img and first_img.image:
            request = self.context.get("request")
            url = first_img.image.url
            return request.build_absolute_uri(url) if request else url
        return None
        
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Название продукта должно содержать минимум 3 символа")
        return value.strip()
        
    def validate_price(self, value):
        try:
            float(value)
        except ValueError:
            raise serializers.ValidationError("Цена должна быть числом")
        return value


class ProductCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        help_text="Список изображений продукта"
    )
    
    class Meta:
        model = Product
        fields = [
            'title', 'description', 'category', 'types_product', 
            'price', 'is_active', 'images'
        ]
        
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Название продукта должно содержать минимум 3 символа")
        return value.strip()
        
    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Описание должно содержать минимум 10 символов")
        return value.strip()
        
    def validate_price(self, value):
        try:
            price_float = float(value)
            if price_float <= 0:
                raise serializers.ValidationError("Цена должна быть положительным числом")
        except ValueError:
            raise serializers.ValidationError("Цена должна быть числом")
        return value
        
    def validate_category(self, value):
        if not Category.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Указанная категория не существует")
        return value
        
    def validate_types_product(self, value):
        if not Types.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Указанный тип не существует")
        return value
        
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        product = Product.objects.create(**validated_data)
        
        for image in images_data:
            ProductImage.objects.create(product=product, image=image)
            
        return product