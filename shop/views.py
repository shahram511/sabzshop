from copyreg import clear_extension_cache
from tkinter import Toplevel
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import *
from cart.cart import Cart
from django.views.decorators.http import require_POST
from order.forms import VerifyPhoneForm
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from random import randint
from datetime import timedelta
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from order.models import ShopUser, Order, OrderItem
from shop.forms import ProfileForm, ReturnProductForm, CommentForm

# Create your views here.




def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.all()
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    inventory_filter =request.GET.get('inventory',None)
    if inventory_filter=='in_stock':
        products = products.filter(inventory__gt=0)
    elif inventory_filter=='out_of_stock':
        products = products.filter(inventory=0)
        
    context = {
        'products': products,
        'category': category,
        'categories': categories,
        'inventory_filter': inventory_filter
    }
    return render(request, 'shop/product_list.html', context)
    


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug)
    
    # get product tags ids--------------------------------
    product_tag_ids = product.tags.values_list('id', flat=True)
    # get similar products--------------------------------
    if product_tag_ids:
        similar_products = Product.objects.filter(tags__id__in=product_tag_ids).exclude(id=product.id).annotate(
            matching_tags=Count('tags', filter=Q(tags__id__in=product_tag_ids))).order_by('-matching_tags', '-created')[:4]
    else:
        similar_products = Product.objects.exclude(id=product.id).order_by('-created')[:4]
    # -------------------------------------------------------
    # Get comments for this product
    comments = product.comments.all()
    # Create comment form with product initial value
    form = CommentForm(initial={'product': product.id})
    
    # Check if user has purchased this product
    has_purchased = False
    if request.user.is_authenticated:
        has_purchased = OrderItem.objects.filter(
            product=product,
            order__buyer=request.user,
            order__paid=True
        ).exists()
    
    context = {
        'product': product,
        'similar_products': similar_products,
        'form': form,
        'comments': comments,
        'has_purchased': has_purchased,
    }
    return render(request, 'shop/product_detail.html', context)

def register(request):
    """
    Simple phone login/register
    """
    # If already logged in, redirect to product list
    if request.user.is_authenticated:
        return redirect('shop:product_list')
    
    if request.method == 'POST':
        form = VerifyPhoneForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            
            # Generate verification code----------------------
            token = str(randint(100000, 999999))
            request.session['login_phone'] = phone
            request.session['login_code'] = token
            request.session['login_code_created'] = timezone.now().isoformat()
            # -------------------------------------------------
            # Print code for testing (remove in production)
            print(f"Login code for {phone}: {token}")
            
            # send sms to phone--------------------------------------
            # from order.sms import send_sms
            # send_sms(phone, f'کد ورود شما: {token}')
            # -------------------------------------------------------
            messages.success(request, f'کد ورود به شماره {phone} ارسال شد')
            return redirect('shop:verify_login')
    else:
        form = VerifyPhoneForm()
    
    return render(request, 'shop/register.html', {'form': form})


def verify_login(request):
    """
    Verify login code and log user in
    """
    # If already logged in, redirect-------------------------
    if request.user.is_authenticated:
        return redirect('shop:product_list')
    # -------------------------------------------------------
    # Get session data---------------------------------------
    phone = request.session.get('login_phone')
    code = request.session.get('login_code')
    code_created = request.session.get('login_code_created')
    # -------------------------------------------------------
    # Check if phone and code are in session-----------------------------
    if not phone or not code:
        messages.error(request, 'لطفا ابتدا شماره تلفن خود را وارد کنید')
        return redirect('shop:register')
    # -------------------------------------------------------
    # Calculate lifetime---------------------------------------
    lifetime = timedelta(minutes=2)
    expires_at = None
    remaining_seconds = None
    
    if code_created:
        created_at = timezone.datetime.fromisoformat(code_created)
        expires_at = created_at + lifetime
        remaining = expires_at - timezone.now()
        remaining_seconds = max(0, int(remaining.total_seconds()))
    # -------------------------------------------------------
    # get the code from the request--------------------------------
    if request.method == 'POST':
        entered_code = request.POST.get('code')
    # -------------------------------------------------------
        if entered_code:
            # Check if code created--------------------------------
            if code_created:
                created_at = timezone.datetime.fromisoformat(code_created)
                # Check if code expired--------------------------------
                if timezone.now() > created_at + lifetime:
                    messages.error(request, 'کد ورود منقضی شده است')
                    # session clear--------------------------------
                    request.session.pop('login_phone', None)
                    request.session.pop('login_code', None)
                    request.session.pop('login_code_created', None)
                    # -------------------------------------------------------
                    return redirect('shop:register')
            # -------------------------------------------------------
            # Verify code--------------------------------------------
            if entered_code == code:
                # Code is correct - login or create user----------------
                user, created = ShopUser.objects.get_or_create(
                    phone=phone,
                    defaults={
                        'first_name': '',
                        'last_name': '',
                        'address': '',
                        'city': ''
                    }
                )
                
                # Set password to code (or use a default)
                if created:
                    user.set_password(code)
                    user.save()
                    messages.success(request, 'حساب کاربری شما ایجاد شد')
                else:
                    messages.success(request, 'ورود موفقیت آمیز بود')
                
                # Login user
                login(request, user)
                
                # Clear session
                request.session.pop('login_phone', None)
                request.session.pop('login_code', None)
                request.session.pop('login_code_created', None)
                
                return redirect('shop:product_list')
            else:
                messages.error(request, 'کد ورود صحیح نیست')
        else:
            messages.error(request, 'لطفا کد ورود را وارد کنید')
    
    context = {
        'phone': phone,
        'expires_at': expires_at,
        'remaining_seconds': remaining_seconds,
        'lifetime_minutes': int(lifetime.total_seconds() // 60),
    }
    return render(request, 'shop/verify_login.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, 'خروج موفقیت آمیز بود')
    return redirect('shop:product_list')

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'پروفایل شما با موفقیت ثبت شد')
            return redirect('shop:profile')
    else:
        request.user.refresh_from_db()
        form = ProfileForm(instance=request.user)
    context = {
        'form': form,
        'orders': Order.objects.filter(buyer=request.user,paid=True),
    }
    return render(request, 'shop/profile.html', context)

@login_required
def return_product_by_user(request):
    if request.method == 'POST':
        form = ReturnProductForm(request.POST)
        if form.is_valid():
            order_item_id = form.cleaned_data['order_item_id']
            reason = form.cleaned_data['reason']
            
            

            try:
                order_item = OrderItem.objects.select_related('order', 'product').get(
                    id=order_item_id,
                    order__buyer=request.user
                )
            except OrderItem.DoesNotExist:
                messages.error(request, 'آیتم سفارش مورد نظر وجود ندارد')
                return redirect('shop:return_product')
            
            order = order_item.order
                        
            # Check if 7 minutes have passed since order creation (for testing - change to days=7 for production)
            time_since_order = timezone.now() - order.created
            if time_since_order < timedelta(days=7):
                remaining_days = int((timedelta(days=7) - time_since_order).total_seconds() / 86400)
                messages.error(
                    request, 
                    f'شما فقط می‌توانید بعد از ۷ روز از تاریخ سفارش، محصول را برگردانید. ({remaining_days} روز باقی مانده)'
                )
                return redirect('shop:return_product')
            
            # Check if order status is NOT shipped
            if order.order_status == 'shipped':
                messages.error(request, 'محصول ارسال شده قابل بازگشت نیست')
                return redirect('shop:return_product')

            if order.order_status == 'returned':
                messages.error(request, 'محصول قبلا بازگشت داده شده است')
                return redirect('shop:return_product')
            
            if order.order_status == 'delivered':
                messages.error(request, 'محصول تحویل داده شده قابل بازگشت نیست')
                return redirect('shop:return_product')
            
            # Process return: Update inventory
            product = order_item.product
            product.inventory += order_item.quantity
            product.save()
            
            # Update order status to returned
            order.order_status = 'returned'
            order.return_reason = reason
            order.save()
            
            messages.success(request, 'وضعیت سفارش به بازگشت تغییر کرد و موجودی محصول بروزرسانی شد')
            return redirect('shop:profile')
    
    # GET request or form invalid - show the form and eligible orders
    form = ReturnProductForm()

    # Get eligible orders for return (7+ minutes old, not shipped, paid, belongs to user)
    # Change timedelta(minutes=7) to timedelta(days=7) for production
    seven_days_ago = timezone.now() - timedelta(days=7)
    eligible_orders = Order.objects.filter(
        buyer=request.user,
        paid=True,
        created__lte=seven_days_ago,
        order_status__in=['pending', 'confirmed']  # Fixed: Only pending/confirmed orders can be returned
    ).prefetch_related('items__product')
        
    # Get returned orders for display
    returned_orders = Order.objects.filter(
        buyer=request.user,
        order_status='returned'
    ).prefetch_related('items__product').order_by('-updated')
    
    context = {
        'form': form,
        'eligible_orders': eligible_orders,
        'returned_orders': returned_orders,
    }
    return render(request, 'shop/return_product.html', context)


@login_required
def add_to_favorite(request):
    product_id = request.POST.get('product_id')
    if product_id is not None:
        product = get_object_or_404(Product, id=product_id)
        user=request.user
        if product in user.favorite_products.all():
            user.favorite_products.remove(product)
            saved=False
        else:
            user.favorite_products.add(product)
            saved=True
        return JsonResponse({'saved': saved})
    
    return JsonResponse({'error': 'Product ID is required'})


@login_required
def add_comment(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            
            # Check if user has purchased this product
            has_purchased = OrderItem.objects.filter(
                product=product,
                order__buyer=request.user,
                order__paid=True
            ).exists()
            
            if not has_purchased:
                messages.error(request, 'شما باید این محصول را خریداری کرده باشید تا بتوانید نظر خود را ثبت کنید.')
                return redirect('shop:product_detail', id=product.id, slug=product.slug)
            
            comment = form.save(commit=False)
            comment.user = request.user
            # product is already set from the form
            comment.save()
            messages.success(request, 'نظر شما با موفقیت ثبت شد')
            return redirect('shop:product_detail', id=comment.product.id, slug=comment.product.slug)
        else:
            # If form is invalid, redirect back to product detail with error
            product_id = form.cleaned_data.get('product') if form.cleaned_data else request.POST.get('product')
            if product_id:
                product = get_object_or_404(Product, id=product_id)
                messages.error(request, 'لطفاً نظر خود را وارد کنید')
                return redirect('shop:product_detail', id=product.id, slug=product.slug)
    # This shouldn't normally be reached, but handle it anyway
    return redirect('shop:product_list')
