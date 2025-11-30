from django.urls import path
from . import views


app_name = 'order'

urlpatterns = [
    path('verify_phone/', views.verify_phone, name='verify_phone'),
    path('verify_code/', views.verify_code, name='verify_code'),
    path('create_order/', views.create_order, name='create_order'),
    
    path('request_payment/', views.send_request, name='request_payment'),
    path('verify_payment/', views.verify , name='verify_payment'),
    path('order_list/', views.order_list, name='order_list'),
    path('order_detail/<int:id>/', views.order_detail, name='order_detail'),
    path('invoice/<int:id>/', views.invoice, name='invoice'),
]