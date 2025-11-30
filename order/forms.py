from django import forms
from .models import Order



class VerifyPhoneForm(forms.Form):
    phone = forms.CharField(label='شماره تلفن', max_length=11, min_length=11)
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isdigit():
            raise forms.ValidationError('شماره تلفن باید عدد باشد')
        if not phone.startswith('09'):
            raise forms.ValidationError('شماره تلفن باید با 09 شروع شود')
        if len(phone) != 11:
            raise forms.ValidationError('شماره تلفن باید 11 رقم باشد')
        return phone
    
    
    
class CreateOrderForm(forms.ModelForm):
    discount_code = forms.CharField(
        required=False,
        label='کد تخفیف',
        widget=forms.TextInput(attrs={
            'class': 'form-control discount-input',
            'placeholder': 'کد تخفیف خود را وارد کنید'
        })
    )
    
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'postal_code', 'city']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
        }