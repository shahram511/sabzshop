from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import ShopUser
from django.core.exceptions import ValidationError


class ShopUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = ShopUser
        fields = ['phone', 'first_name', 'last_name', 'address']
        
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if self.instance.pk:
            if ShopUser.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
                raise ValidationError('This phone number is already in use.')
        else:
            if ShopUser.objects.filter(phone=phone).exists():
                raise ValidationError('This phone number is already in use.')
        if not phone.isdigit():
            raise ValidationError('phone must be digits only.')
        if not phone.startswith('09'):
            raise ValidationError('phone must start with 09.')
        if len(phone) != 11:
            raise ValidationError('phone must be 11 digits.')
        return phone
        
class ShopUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = ShopUser
        fields = ['phone', 'first_name', 'last_name', 'address']
        
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if self.instance.pk:
            if ShopUser.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
                raise ValidationError('This phone number is already in use.')
        else:
            if ShopUser.objects.filter(phone=phone).exists():
                raise ValidationError('This phone number is already in use.')
        if not phone.isdigit():
            raise ValidationError('phone must be digits only.')
        if not phone.startswith('09'):
            raise ValidationError('phone must start with 09.')
        if len(phone) != 11:
            raise ValidationError('phone must be 11 digits.')
        return phone
        