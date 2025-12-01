from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .serializers import ProductSerializer, ShopListSerializer, UserRegisterSerializer, OrderSerializer, CategorySerializer

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from account.models import ShopUser
from shop.models import Product, Category
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
    
    @extend_schema(
        summary="Get all products with discount",
        description = "Returns all products with discount greater than the minimum discount",
        parameters=[
            OpenApiParameter(
                name='min_discount', 
                description='Minimum discount', 
                location=OpenApiParameter.QUERY,
                required=False, 
                type=OpenApiTypes.INT,
            ),
        ],
        responses={200: ProductSerializer(many=True), 400: 'Invalid discount'},
    )
        
    @action(detail=False, methods=['get'],permission_classes=[AllowAny])
    def discount_products(self, request):
        min_discount = request.query_params.get('min_discount', 0)
        try:
            min_discount = int(min_discount)
        except ValueError:
            return Response({'error': 'min_discount must be an integer'}, status=400)
        
        products = self.queryset.filter(off__gt=min_discount)
        if not products.exists():
            return Response({'error': 'No products found with discount greater than the minimum discount'}, status=400)
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
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter orders to only show orders belonging to the authenticated buyer.
        """
        return Order.objects.filter(buyer=self.request.user)
    
class OrderDetailAPIView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsBuyer]
    
    def get_queryset(self):
        """
        Filter orders to only show orders belonging to the authenticated buyer.
        """
        return Order.objects.filter(buyer=self.request.user)
    

    
class CategoryListAPIView(generics.ListAPIView):
    """
    list all available categories whit their IDs
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]