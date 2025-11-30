from django.db import models
from shop.models import Product
from account.models import ShopUser
from django.utils import timezone
# Create your models here.


class Order(models.Model):
    order_status = models.CharField(max_length=100, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'), 
        ('cancelled', 'Cancelled'), 
        ('returned', 'Returned')], default='pending'
    )
    buyer = models.ForeignKey(ShopUser, related_name='orders', on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=11)
    email = models.EmailField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    return_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created']
        indexes = [models.Index(fields=['-created'])]
        
    def __str__(self):
        return f'Order {self.id}'
    
    def get_total_price(self):
        return sum(item.get_cost() for item in self.items.all())
    
    def get_post_price  (self):
        weight = sum(item.get_weight() for item in self.items.all())
        if weight <= 3000:
            return 50
        elif 3000 < weight < 5000:
            return 60
        else:
            return 70
        
    def get_total_price_with_post(self):
        return self.get_total_price() + self.get_post_price()

        
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=1)
    weight = models.PositiveIntegerField(default=0)
        
    def __str__(self):
        return str(self.id)
            
    def get_cost(self):
        return self.price * self.quantity
    
    def get_weight(self):
        return self.weight * self.quantity
    
class Transaction(models.Model):
    order = models.ForeignKey(Order, related_name='transactions', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=100, choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending')

    def __str__(self):
        return f'Transaction {self.id} for Order {self.order.id}'


class DiscountCode(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name='کد تخفیف')
    discount_percent = models.PositiveIntegerField(default=0, verbose_name='درصد تخفیف')
    discount_amount = models.PositiveIntegerField(default=0, verbose_name='مبلغ تخفیف')
    min_purchase = models.PositiveIntegerField(default=0, verbose_name='حداقل خرید')
    max_discount = models.PositiveIntegerField(default=0, verbose_name='حداکثر تخفیف')
    valid_from = models.DateTimeField(verbose_name='تاریخ شروع')
    valid_to = models.DateTimeField(verbose_name='تاریخ پایان')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    usage_limit = models.PositiveIntegerField(default=0, verbose_name='حد استفاده')
    used_count = models.PositiveIntegerField(default=0, verbose_name='تعداد استفاده شده')
    
    class Meta:
        verbose_name = 'کد تخفیف'
        verbose_name_plural = 'کدهای تخفیف'
    
    def __str__(self):
        return self.code
    
    def is_valid(self, total_price):
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_to and
            total_price >= self.min_purchase and
            (self.usage_limit == 0 or self.used_count < self.usage_limit)
        )
    
    def calculate_discount(self, total_price):
        if self.discount_percent > 0:
            discount = (total_price * self.discount_percent) // 100
            if self.max_discount > 0:
                discount = min(discount, self.max_discount)
            return discount
        return min(self.discount_amount, total_price)