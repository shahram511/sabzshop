from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('register/', views.register, name='register'),
    path('verify_login/', views.verify_login, name='verify_login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('return_product/', views.return_product_by_user, name='return_product'),
    path('add_to_favorite/', views.add_to_favorite, name='add_to_favorite'),
    path('add_comment/', views.add_comment, name='add_comment'),
]