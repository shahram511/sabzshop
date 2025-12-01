from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'shops', ShopUserViewSet)

app_name = 'api'

urlpatterns = [
    # path('products/', ProductListAPIView.as_view(), name='product_list_api'),
    # path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='product_detail_api'),
    # path('shops/', ShopListAPIView.as_view(), name='shop_list_api'),
    path('categories/', CategoryListAPIView.as_view(), name='category_list_api'),
    path('register/', UserRegisterAPIView.as_view(), name='user_register_api'),
    path('orders/', views.OrderListAPIView.as_view(), name='order_list_api'),
    path('orders/<int:pk>/', views.OrderDetailAPIView.as_view(), name='order_detail_api'),
    path('', include(router.urls)),
]