from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .serializers import ProductSerializer, ShopListSerializer, UserRegisterSerializer, OrderSerializer

from account.models import ShopUser
from shop.models import Product
from order.models import Order
from .permissions import IsAdminFromTehran, IsBuyer

# class ProductDetailAPIView(RetrieveAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer


# class ProductListAPIView(ListAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    @action(detail=False, methods=['get'],permission_classes=[AllowAny])
    def discount_products(self, request):
        min_discount = request.query_params.get('min_discount', 0)
        try:
            min_discount = int(min_discount)
        except ValueError:
            return Response({'error': 'min_discount must be an integer'}, status=400)
        
        products = self.queryset.filter(off__gt=min_discount)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)    
    
    
    
class ShopUserViewSet(viewsets.ModelViewSet):
    queryset = ShopUser.objects.all()
    serializer_class = ShopListSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        if self.action == 'register':
            return UserRegisterSerializer
        return ShopListSerializer
    
    
    
    @action(detail=False, methods=['post'],permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'user created successfully','phone': user.phone}, status=201)
        return Response({'error': serializer.errors}, status=400)

class UserRegisterAPIView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer
    queryset = ShopUser.objects.all()
    

class OrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminFromTehran]
    
class OrderDetailAPIView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsBuyer]
    