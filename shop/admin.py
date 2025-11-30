from django.contrib import admin
from .models import *


# Register your models here.

class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 0

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'new_price', 'off', 'inventory', 'created', 'updated']
    list_filter = ['category', 'created']
    list_editable = ['price', 'new_price', 'off', 'inventory']
    search_fields = ['name', 'description']
    list_per_page = 10
    inlines = [ProductFeatureInline, ProductImageInline]
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'comment', 'created']
    list_filter = ['product', 'user', 'created']
    search_fields = ['product', 'user', 'comment']
    list_per_page = 10
    