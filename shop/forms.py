from django import forms
from .models import Product, Comment
from account.models import ShopUser
from order.models import OrderItem

class VerifyPhoneForm(forms.Form):
    phone = forms.CharField(max_length=11, label='شماره تلفن همراه')
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isdigit():
            raise forms.ValidationError('شماره تلفن همراه باید عدد باشد')
        if len(phone) != 11:
            raise forms.ValidationError('شماره تلفن همراه باید 11 رقم باشد')
        return phone
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = ShopUser
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'phone': 'شماره تلفن همراه',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'email': 'ایمیل',
        }
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isdigit():
            raise forms.ValidationError('شماره تلفن همراه باید عدد باشد')
        if len(phone) != 11:
            raise forms.ValidationError('شماره تلفن همراه باید 11 رقم باشد')
        return phone
    

class ReturnProductForm(forms.Form):
    order_item_id = forms.IntegerField(widget=forms.HiddenInput())
    reason = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),label='علت مرجوع کالا',required=True)
    
    def clean_order_item_id(self):
        order_item_id = self.cleaned_data['order_item_id']
        if not OrderItem.objects.filter(id=order_item_id).exists():
            raise forms.ValidationError('آیتم سفارش مورد نظر وجود ندارد')
        return order_item_id
    
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment','product']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'product': forms.HiddenInput(),
        }
        labels = {
            'comment': 'نظر',
        }