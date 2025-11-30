from random import randint
from django.shortcuts import render, redirect
from django.contrib import messages
from account.models import ShopUser
from .forms import VerifyPhoneForm
from django.contrib.auth import login
from datetime import timedelta
from django.utils import timezone
from sms_ir import SmsIr
from cart.cart import Cart
from .forms import CreateOrderForm
from .models import Order, OrderItem, Transaction, DiscountCode
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests
import json
from django.http import HttpResponse
from order.sms import send_sms
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
# Create your views here.






def verify_phone(request):
    if request.user.is_authenticated:
        return redirect('order:create_order')
    if request.method == 'POST':
        form = VerifyPhoneForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            if ShopUser.objects.filter(phone=phone).exists():
                messages.error(request, 'این شماره تلفن همراه قبلا ثبت شده است')


            token = str(randint(100000, 999999))
            request.session['verify_phone_tokens'] = token
            request.session['verify_phone_tokens_created_at'] = timezone.now().isoformat()
            request.session['phone'] = phone
            

            # _ir = SmsIr('2z6bzhAL0rEjgJLJO3UnZYo2gFBdajuT6ha8narWTHyPcJ3o','30002101005709')
            # sms_ir.send_sms(phone, f'کد تایید شما برای ثبت نام در فروشگاه سبز: {token}', '30002101005709')
            print(token)
            print(phone)

            messages.success(request, 'کد تایید به شماره تلفن همراه شما ارسال شد')
            return redirect('order:verify_code')
    else:
        form = VerifyPhoneForm()
    return render(request, 'verify_phone.html', {'form': form})


def verify_code(request):
    lifetime = timedelta(minutes=2)
    created_at_str = request.session.get('verify_phone_tokens_created_at')
    expires_at = None
    remaining_seconds = None
    if created_at_str:
        created_at = timezone.datetime.fromisoformat(created_at_str)
        expires_at = created_at + lifetime
        remaining = expires_at - timezone.now()
        remaining_seconds = max(0, int(remaining.total_seconds()))

    if request.method == 'POST':
        code = request.POST.get('code')
        if code:
            verify_phone_tokens = request.session.get('verify_phone_tokens')
            created_at_str = request.session.get('verify_phone_tokens_created_at')
            phone = request.session.get('phone')
            if not verify_phone_tokens or not created_at_str or not phone:
                messages.error(request, 'برای دریافت کد تایید ابتدا شماره تلفن خود را وارد کنید')
                return redirect('order:verify_phone')
            created_at = timezone.datetime.fromisoformat(created_at_str)
            if timezone.now() > created_at + lifetime:
                messages.error(request, 'کد تایید منقضی شده است، دوباره درخواست دهید.')
                request.session.pop('verify_phone_tokens', None)
                request.session.pop('verify_phone_tokens_created_at', None)
                request.session.pop('phone', None)
                return redirect('order:verify_phone')
            if code == verify_phone_tokens:
                messages.success(request, 'کد تایید با موفقیت تایید شد')
                user, created = ShopUser.objects.get_or_create(
                    phone=phone,
                    defaults={'first_name': '', 'last_name': '', 'address': ''},
                )
                if created:
                    user.set_password(code)
                    user.save()
                    # sms_ir = SmsIr('2z6bzhAL0rEjgJLJO3UnZYo2gFBdajuT6ha8narWTHyPcJ3o','30002101005709')
                    # sms_ir.send_sms(phone, f'کد تایید شما برای ثبت نام در فروشگاه سبز: {code}', '30002101005709')

                login(request, user)
                request.session.pop('verify_phone_tokens', None)
                request.session.pop('verify_phone_tokens_created_at', None)
                request.session.pop('phone', None)
                return redirect('order:create_order')
            messages.error(request, 'کد تایید صحیح نیست')
            return redirect('order:verify_code')
        return render(
            request,
            'verify_code.html',
            {
                'expires_at': expires_at,
                'remaining_seconds': remaining_seconds,
                'lifetime_minutes': int(lifetime.total_seconds() // 60),
            },
        )
    return render(
        request,
        'verify_code.html',
        {
            'expires_at': expires_at,
            'remaining_seconds': remaining_seconds,
            'lifetime_minutes': int(lifetime.total_seconds() // 60),
        },
    )

# def verify_code(request):
#     if request.method == 'POST':
#         code = request.POST.get('code')
#         if code:
#             verify_phone_tokens = request.session.get('verify_phone_tokens')
#             phone = request.session.get('phone')
#             verify_phone_tokens_created_at = request.session.get('verify_phone_tokens_created_at')
#             created_at = timezone.datetime.fromisoformat(verify_phone_tokens_created_at)


#             if verify_phone_tokens_created_at and datetime.now().isoformat() - verify_phone_tokens_created_at > timedelta(minutes=1):
#                 messages.error(request, 'کد تایید منقضی شده است')
#                 del request.session['verify_phone_tokens']
#                 del request.session['phone']
#                 del request.session['verify_phone_tokens_created_at']
#                 return redirect('order:verify_code')
            
#             if code == verify_phone_tokens:
#                 messages.success(request, 'کد تایید با موفقیت تایید شد')
#                 user = ShopUser.objects.create(phone=phone, first_name='', last_name='', address='')
#                 user.set_password(code)
#                 user.save()
#                 # send sms to phone
#                 login(request, user)
#                 del request.session['verify_phone_tokens']
#                 del request.session['phone']
#                 return redirect('shop:product_list')
#             else:
#                 messages.error(request, 'کد تایید صحیح نیست')
#                 return redirect('order:verify_code')
#         return render(request, 'verify_code.html')
#     return render(request, 'verify_code.html')

@login_required
def create_order(request):
    cart = Cart(request)
    discount_amount = 0
    final_price = cart.get_final_price()
    discount_error = None
    discount_success = False
    applied_discount_code = None
    
    if request.method == 'POST':
        form = CreateOrderForm(request.POST)
        discount_code = request.POST.get('discount_code', '').strip()
        apply_discount_only = request.POST.get('apply_discount', False)
        
        # Handle discount code
        if discount_code:
            try:
                discount = DiscountCode.objects.get(code=discount_code)
                if discount.is_valid(cart.get_total_price()):
                    discount_amount = discount.calculate_discount(cart.get_total_price())
                    final_price = cart.get_final_price() - discount_amount
                    discount_success = True
                    applied_discount_code = discount_code
                    request.session['discount_code'] = discount_code
                    request.session['discount_amount'] = discount_amount
                    if apply_discount_only:
                        messages.success(request, f'کد تخفیف "{discount_code}" با موفقیت اعمال شد!')
                else:
                    discount_error = 'کد تخفیف معتبر نیست یا منقضی شده است'
                    if apply_discount_only:
                        messages.error(request, discount_error)
            except DiscountCode.DoesNotExist:
                discount_error = 'کد تخفیف یافت نشد'
                if apply_discount_only:
                    messages.error(request, discount_error)
        
        # If only applying discount, don't process the order
        if apply_discount_only:
            context = {
                'form': form,
                'cart': cart,
                'discount_amount': discount_amount,
                'final_price': final_price,
                'discount_error': discount_error,
                'discount_success': discount_success,
            }
            return render(request, 'create_order.html', context)
        
        if form.is_valid():
            order = form.save()
            order.buyer = request.user
            order.save()
            
            # Apply discount if exists
            if applied_discount_code:
                try:
                    discount = DiscountCode.objects.get(code=applied_discount_code)
                    discount.used_count += 1
                    discount.save()
                except DiscountCode.DoesNotExist:
                    pass
            
            for item in cart:
                OrderItem.objects.create(order=order, 
                                         product=item['product'], 
                                         price=item['price'], 
                                         quantity=item['quantity'], 
                                         weight=item['weight'])
            cart.clear()
            
            # Clear discount from session
            request.session.pop('discount_code', None)
            request.session.pop('discount_amount', None)
            
            request.session['order_id'] = order.id
            messages.success(request, 'سفارش با موفقیت ثبت شد')
            return redirect('order:request_payment')
    else:
        # Check if there's a discount code in session
        if 'discount_code' in request.session:
            try:
                discount = DiscountCode.objects.get(code=request.session['discount_code'])
                if discount.is_valid(cart.get_total_price()):
                    discount_amount = request.session.get('discount_amount', 0)
                    final_price = cart.get_final_price() - discount_amount
                    discount_success = True
                    applied_discount_code = request.session['discount_code']
            except DiscountCode.DoesNotExist:
                pass
        
        # Refresh user data from database to get latest information
        request.user.refresh_from_db()
        
        # Try to get the user's last order to pre-fill with previous order data
        last_order = Order.objects.filter(buyer=request.user).order_by('-created').first()
        
        initial_data = {}
        if last_order:
            # Pre-fill form with last order data (includes postal_code)
            initial_data = {
                'first_name': last_order.first_name or request.user.first_name or '',
                'last_name': last_order.last_name or request.user.last_name or '',
                'email': last_order.email or request.user.email or '',
                'phone': last_order.phone or request.user.phone or '',
                'city': last_order.city or request.user.city or '',
                'address': last_order.address or request.user.address or '',
                'postal_code': last_order.postal_code or '',
            }
        else:
            # No previous orders - use user profile data
            initial_data = {
                'first_name': request.user.first_name or '',
                'last_name': request.user.last_name or '',
                'email': request.user.email or '',
                'phone': request.user.phone or '',
            }
        
        if applied_discount_code:
            initial_data['discount_code'] = applied_discount_code
        
        form = CreateOrderForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart': cart,
        'discount_amount': discount_amount,
        'final_price': final_price,
        'discount_error': discount_error,
        'discount_success': discount_success,
    }
    return render(request, 'create_order.html', context)





#? sandbox merchant 
SANDBOX_MODE = getattr(settings, 'SANDBOX', True)
sandbox = 'sandbox' if SANDBOX_MODE else 'www'

# Zarinpal API endpoints
# Try v4 API format first (newer format)
ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/v4/payment/verify.json"
# Alternative format if v4 doesn't work: f"https://{sandbox}.zarinpal.com/pg/rest/PaymentRequest.json"
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"

# Important: need to edit for real server.
CallbackURL = 'http://127.0.0.1:8000/order/verify_payment/'


def send_request(request):
    order = Order.objects.get(id=request.session['order_id'])
    description = ""
    for item in order.items.all():
        description += item.product.name
    
    merchant_id = getattr(settings, 'MERCHANT', None)
    if not merchant_id:
        return HttpResponse('Error: Merchant ID is not configured')
    
    # Zarinpal v4 API requires different structure - merchant_id in URL or as merchant_id field
    # Try with merchant_id as a field (v4 format)
    data = {
        "merchant_id": merchant_id,  # v4 API uses lowercase with underscore
        "amount": order.get_total_price_with_post(),
        "description": description,
        "callback_url": CallbackURL,
        "metadata": {
            "mobile": request.user.phone,
        }
    }
    
    headers = {
        'accept': 'application/json', 
        'content-type': 'application/json'
    }
    
    try:
        # Use json= parameter - requests will automatically serialize and set content-type
        response = requests.post(ZP_API_REQUEST, json=data, headers=headers, timeout=10)

        if response.status_code == 200:
            try:
                response_json = response.json()
                # v4 API response structure
                data = response_json.get('data', {})
                authority = data.get('authority') or response_json.get('authority')
                errors = response_json.get('errors', {})
                
                if authority:
                    return redirect(ZP_API_STARTPAY + authority)
                else:
                    # Handle different error statuses
                    return HttpResponse(
                        f'Payment request failed. Errors: {errors}'
                    )
            except (json.JSONDecodeError, KeyError) as e:
                return HttpResponse(f'Error parsing response: {str(e)}')
        else:
            # More detailed error information
            try:
                error_detail = response.json()
                return HttpResponse(
                    f'Response failed with status {response.status_code}: {error_detail}'
                )
            except:
                return HttpResponse(
                    f'Response failed with status {response.status_code}: {response.text}'
                )
                
    except requests.exceptions.Timeout:
        return HttpResponse('Timeout Error: The payment gateway did not respond in time')
    except requests.exceptions.ConnectionError:
        return HttpResponse('Connection Error: Could not connect to payment gateway')
    except Exception as e:
        return HttpResponse(f'Unexpected error: {str(e)}')


def verify(request):
    order = Order.objects.get(id=request.session['order_id'])
    merchant_id = getattr(settings, 'MERCHANT', None)
    
    if not merchant_id:
        return HttpResponse('Error: Merchant ID is not configured')

    # v4 API format
    data = {
        "merchant_id": merchant_id,  # v4 API uses lowercase with underscore
        "amount": order.get_total_price_with_post(),
        "authority": request.GET.get('Authority'),
    }
    
    headers = {
        'accept': 'application/json', 
        'content-type': 'application/json'
    }
    
    try:
        # Use json= parameter instead of data with json.dumps
        response = requests.post(ZP_API_VERIFY, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            try:
                
                response_json = response.json()
                # v4 API response structure
                data = response_json.get('data', {})
                reference_id = data.get('ref_id') or response_json.get('ref_id')
                errors = response_json.get('errors', {})
                
                if reference_id and not errors:

                    # Payment successful - update inventory and mark order as paid
                    for item in order.items.all():
                        item.product.inventory -= item.quantity
                        item.product.save()
                    order.paid = True
                    order.save()
                    request.session.pop('order_id', None)
                    
                # send sms to buyer-------------------------------
                if order.buyer and order.buyer.phone:
                    try:
                        send_sms(order.buyer.phone, f'Order {order.id} paid successfully')
                        print(f'SMS sent to {order.buyer.phone}: {f'Order {order.id} paid successfully'}')
                    except Exception as e:
                        print(f'Error sending SMS: {e}')
                        
                # send email to buyer-------------------------------
                if order.email :
                    try:
                        send_mail('Order paid successfully', f'Order {order.id} paid successfully', settings.EMAIL_HOST_USER, [order.email], fail_silently=False)
                        print(f'Email sent to {order.email}: {f'Order {order.id} paid successfully'}')
                    except Exception as e:
                        print(f'Error sending email: {e}')
                #---------------------------------------------------      
                  
                    return render(request, 'payment_tracking.html', {
                        'reference_id': reference_id,
                        'success': True,
                        'order_id': order.id,
                        'order': order
                    })
                else:
                    return render(request, 'payment_tracking.html', {'success': False})

            except (json.JSONDecodeError, KeyError) as e:
                return HttpResponse(f'Error parsing response: {str(e)}')
        else:
            try:
                error_detail = response.json()
                return HttpResponse(
                    f'Response failed with status {response.status_code}: {error_detail}'
                )
            except:
                return HttpResponse(
                    f'Response failed with status {response.status_code}: {response.text}'
                )
                
    except requests.exceptions.Timeout:
        return HttpResponse('Timeout Error: The payment gateway did not respond in time')
    except requests.exceptions.ConnectionError:
        return HttpResponse('Connection Error: Could not connect to payment gateway')
    except Exception as e:
        return HttpResponse(f'Unexpected error: {str(e)}') 


def order_list(request):
    orders = Order.objects.filter(buyer=request.user,paid=True)
    return render(request, 'order_list.html', {'orders': orders})

@login_required
def order_detail(request, id):
    order = get_object_or_404(Order, id=id, buyer=request.user)
    return render(request, 'order_detail.html', {'order': order})

@login_required
def invoice(request, id):
    order = get_object_or_404(Order, id=id, buyer=request.user,paid=True)
    return render(request, 'invoice.html', {'order': order})
