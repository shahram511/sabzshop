from rest_framework import serializers
from shop.models import Product, ProductFeature, ProductImage, Category
from account.models import ShopUser
from order.models import Order

class ProductFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFeature
        fields = ['id', 'name', 'value']
        
        
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
        
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(),source='category',write_only=True, required=True)
    features = ProductFeatureSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'new_price', 'description', 'category', 'weight', 'price', 'off', 'inventory', 'features', 'images', 'category_id']


class ShopListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopUser
        fields = ['first_name', 'phone', 'last_name', 'address', 'is_active', 'is_staff', 'is_superuser', 'date_joined']

class UserRegisterSerializer(serializers.ModelSerializer):
    password_confirmation = serializers.CharField(write_only=True,required=True)
    class Meta:
        model = ShopUser
        fields = [ 'phone', 'password', 'password_confirmation']
        extra_kwargs = {
            'password': {'write_only': True},
        }
        
    def create(self, validated_data):
        validated_data.pop('password_confirmation')
        user = ShopUser(phone=validated_data['phone'],)
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirmation']:
            raise serializers.ValidationError("Password and confirm password do not match")
        return attrs
        
        
    def validate_phone(self, value):
        if ShopUser.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number already exists")
        if len(value) != 11:
            raise serializers.ValidationError("Phone number must be 11 digits")
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must be digits")
        if not value.startswith('09'):
            raise serializers.ValidationError("Phone number must start with 09")
        return value
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit")
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Password must contain at least one letter")
        return value
    
    
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'buyer', 'first_name', 'last_name', 'phone', 'email', 'city', 'province', 'address', 'postal_code', 'created', 'updated', 'paid']

        