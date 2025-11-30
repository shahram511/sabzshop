from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .cart import Cart
from shop.models import Product
from django.views.decorators.http import require_POST
from django.http import JsonResponse
# Create your views here.


@require_POST
def cart_add(request, product_id):
        try:
            cart = Cart(request)
            product = get_object_or_404(Product, id=product_id)
            # Check if product is out of stock-------------
            if product.inventory == 0:
                return JsonResponse({'success': False, 'error': 'محصول مورد نظر موجود نیست'})
            # ---------------------------------------------
            # Check if product was actually added (inventory limit check)
            added = cart.add(product)
            if not added:
                # Get current quantity in cart
                product_id = str(product.id)
                current_quantity = cart.cart.get(product_id, {}).get('quantity', 0)
                return JsonResponse({
                    'success': False, 
                    'error': f'تعداد موجودی محصول {product.name} به پایان رسیده است. شما {current_quantity} عدد در سبد خرید دارید.'
                })
            
            context = {
                'success': True,
                'item_count': len(cart),
                'total_price': cart.get_total_price(),
            }
            return JsonResponse(context)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
def cart_detail(request):
    cart = Cart(request)
    context = {
        'cart': cart,
    }
    return render(request,'cart/cart_detail.html', context)
    


@require_POST
def update_quantity(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    action = request.POST.get('action')

    if action == 'add':
        added = cart.add(product)
        if not added:
            product_id_str = str(product.id)
            current_quantity = cart.cart.get(product_id_str, {}).get('quantity', 0)
            return JsonResponse({
                'ok': False,
                'error': f'تعداد موجودی محصول {product.name} به پایان رسیده است. شما {current_quantity} عدد در سبد خرید دارید.'
            })
    elif action == 'subtract':
        cart.decrease(product)
    elif action == 'remove':
        cart.remove(product)
        
    request.session['cart'] = cart.cart
    cart.save()

    return JsonResponse({'ok': True})