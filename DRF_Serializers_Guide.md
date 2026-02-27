# Django Rest Framework: Сериализаторы и Оптимизация

## Оглавление
1. [Сериализаторы в Django Rest Framework](#сериализаторы)
2. [Сериализация моделей](#сериализация-моделей)
3. [Оптимизация Django](#оптимизация-django)
4. [Кэширование](#кэширование)
5. [Создание товаров через POST запрос](#создание-товаров)

## Сериализаторы

Сериализаторы в DRF преобразуют сложные типы данных (например, модели Django) в нативные типы Python, которые затем могут быть легко преобразованы в JSON.

### Типы сериализаторов:
- **ModelSerializer** - автоматически создает поля на основе модели
- **Serializer** - базовый класс для полной кастомизации
- **ListSerializer** - для работы со списками объектов

### Основные компоненты сериализатора:

```python
class ProductSerializer(serializers.ModelSerializer):
    # Поля только для чтения
    category_title = serializers.CharField(source='category.title', read_only=True)
    
    # Метод-поля для кастомной логики
    first_image = serializers.SerializerMethodField()
    
    # Вложенные сериализаторы
    images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'category_title', 'first_image', 'images']
```

## Сериализация моделей

### Enhanced сериализаторы с валидацией:

```python
class ProductCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Product
        fields = ['title', 'description', 'category', 'types_product', 'price', 'images']
    
    # Валидация полей
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Минимум 3 символа")
        return value.strip()
    
    def validate_price(self, value):
        try:
            price_float = float(value)
            if price_float <= 0:
                raise serializers.ValidationError("Цена должна быть положительной")
        except ValueError:
            raise serializers.ValidationError("Цена должна быть числом")
        return value
    
    # Кастомное создание
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        product = Product.objects.create(**validated_data)
        
        for image in images_data:
            ProductImage.objects.create(product=product, image=image)
        
        return product
```

## Оптимизация Django

### 1. Оптимизация запросов к базе данных

#### select_related - для ForeignKey и OneToOne
```python
# Вместо N+1 запросов
products = Product.objects.all()  # N запросов к category + N запросов к types_product

# Используем select_related
products = Product.objects.select_related('category', 'types_product').all()  # 1 запрос
```

#### prefetch_related - для ManyToMany и обратных связей
```python
# Вместо N запросов к images
products = Product.objects.all()  # N запросов к images

# Используем prefetch_related
products = Product.objects.prefetch_related('images').all()  # 2 запроса

# Комбинированный подход
products = Product.objects.select_related(
    'category', 'types_product'
).prefetch_related(
    Prefetch('images', queryset=ProductImage.objects.all())
).all()
```

### 2. Оптимизация полей

#### only() и defer()
```python
# Загрузить только нужные поля
products = Product.objects.only('id', 'title', 'price').all()

# Исключить тяжелые поля
products = Product.objects.defer('description', 'created_at').all()
```

## Кэширование

### 1. Кэширование представлений

```python
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

@method_decorator(cache_page(60 * 15), name='dispatch')  # 15 минут
class ProductAPIView(ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
```

### 2. Кэширование запросов

```python
from django.core.cache import cache

def get_cached_products():
    cache_key = 'product_list'
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        products = Product.objects.select_related('category').all()
        serializer = ProductSerializer(products, many=True)
        cached_data = serializer.data
        cache.set(cache_key, cached_data, 60 * 5)  # 5 минут
    
    return cached_data
```

### 3. Инвалидация кэша

```python
# При создании/обновлении/удалении
def invalidate_product_cache():
    cache.delete('product_list')
    cache.delete('category_list')
```

## Создание товаров через POST запрос

### API Endpoint: `/api/product/product-create/`

### Пример POST запроса:

```bash
curl -X POST http://localhost:8000/api/product/product-create/ \
  -H "Content-Type: multipart/form-data" \
  -F "title=Новый товар" \
  -F "description=Описание нового товара" \
  -F "category=1" \
  -F "types_product=1" \
  -F "price=1500.00" \
  -F "is_active=true" \
  -F "images=@image1.jpg" \
  -F "images=@image2.jpg"
```

### Пример JSON запроса:

```json
POST /api/product/product-create/
Content-Type: application/json

{
    "title": "Смартфон iPhone 15",
    "description": "Новый смартфон Apple с улучшенной камерой",
    "category": 1,
    "types_product": 2,
    "price": "99999.00",
    "is_active": true,
    "images": [
        "base64_encoded_image_or_file_upload"
    ]
}
```

### Ответ при успешном создании:

```json
{
    "id": 123,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Смартфон iPhone 15",
    "description": "Новый смартфон Apple с улучшенной камерой",
    "category": 1,
    "category_title": "Электроника",
    "types_product": 2,
    "types_title": "Смартфоны",
    "price": "99999.00",
    "is_active": true,
    "created_at": "2024-02-27T12:00:00Z",
    "first_image": "http://localhost:8000/media/product/iphone15_1.jpg",
    "images": [
        {
            "id": 456,
            "image_url": "http://localhost:8000/media/product/iphone15_1.jpg"
        },
        {
            "id": 457,
            "image_url": "http://localhost:8000/media/product/iphone15_2.jpg"
        }
    ]
}
```

### Ошибки валидации:

```json
{
    "title": ["Название продукта должно содержать минимум 3 символа"],
    "price": ["Цена должна быть положительным числом"],
    "category": ["Указанная категория не существует"]
}
```

## Доступные эндпоинты:

1. **GET** `/api/product/category-list/` - Список категорий (кэш 15 мин)
2. **GET** `/api/product/type-list/` - Список типов (кэш 10 мин)
3. **GET** `/api/product/product-list/` - Список товаров (кэш 5 мин)
4. **POST** `/api/product/product-create/` - Создание нового товара

## Настройки кэширования в settings.py:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Для Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

## Лучшие практики:

1. **Всегда используйте select_related/prefetch_related** для связанных данных
2. **Кэшируйте только стабильные данные** (не меняющиеся часто)
3. **Используйте appropriate cache timeout** в зависимости от данных
4. **Валидируйте входные данные** на уровне сериализатора
5. **Используйте транзакции** для сложных операций создания
6. **Очищайте кэш** при изменении данных
7. **Оптимизируйте изображения** перед загрузкой
8. **Используйте пагинацию** для больших списков данных
