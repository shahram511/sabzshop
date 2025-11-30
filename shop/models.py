from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager

from account.models import ShopUser
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
        verbose_name = 'دسته بندی'
        verbose_name_plural = 'دسته بندی ها'
        
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name='دسته بندی')
    name = models.CharField(max_length=200, verbose_name='نام')
    slug = models.SlugField(max_length=200, verbose_name='اسلاگ')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    weight = models.PositiveIntegerField(default=0, verbose_name='وزن')
    price = models.PositiveIntegerField(default=0, verbose_name='قیمت')
    off = models.PositiveIntegerField(default=0, verbose_name=' تخفیف')
    new_price = models.PositiveIntegerField(default=0, verbose_name='قیمت جدید')
    tags = TaggableManager()
    favorite_products = models.ManyToManyField(ShopUser, related_name='favorite_products', blank=True)
   
    
    created = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    inventory = models.PositiveIntegerField(default=0, verbose_name='موجودی')
    
    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['id','slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created']),
            
        ]
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])


class ProductFeature(models.Model):
    product = models.ForeignKey('Product', related_name='features', on_delete=models.CASCADE, verbose_name='محصول')
    name = models.CharField(max_length=200, verbose_name='نام')
    value = models.CharField(max_length=200, verbose_name='مقدار')
    class Meta:
        verbose_name = 'مشخصات محصول'
        verbose_name_plural = 'مشخصات محصولات'
    
    def __str__(self):
        return self.name+' : '+self.value    
    
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, verbose_name='محصول')
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, verbose_name='تصویر')
    created = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
   
    
    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]
        verbose_name = 'تصویر محصول'
        verbose_name_plural = 'تصویرهای محصولات'
        

class Comment(models.Model):
    product = models.ForeignKey(Product, related_name='comments', on_delete=models.CASCADE, verbose_name='محصول')
    user = models.ForeignKey(ShopUser, related_name='comments', on_delete=models.CASCADE, verbose_name='کاربر')
    comment = models.TextField(verbose_name='نظر')
    created = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    class Meta:
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]
    def __str__(self):
        return self.comment
    
    