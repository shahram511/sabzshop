from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import ShopUser
from account.forms import ShopUserCreationForm, ShopUserChangeForm
# Register your models here.


@admin.register(ShopUser)
class ShopUserAdmin(UserAdmin):
    form = ShopUserChangeForm
    add_form = ShopUserCreationForm
    model = ShopUser
    list_display = ['phone', 'first_name', 'last_name', 'email', 'is_active', 'is_staff']
    ordering = ['phone']
    search_fields = ['phone', 'first_name', 'last_name']
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'address', 'city', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'fields': ('phone', 'password', 'password2')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'address', 'city', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )