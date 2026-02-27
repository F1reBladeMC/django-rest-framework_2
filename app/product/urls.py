from django.urls import path
from app.product.views import CategoryAPIView, TypesAPIView, ProductAPIView, ProductCreateView

urlpatterns = [
    path("category-list", CategoryAPIView.as_view(), name='category-list'),
    path("type-list", TypesAPIView.as_view(), name='type-list'),
    path("product-list", ProductAPIView.as_view(), name='product-list'),
    path("product-create", ProductCreateView.as_view(), name='product-create'),
]
