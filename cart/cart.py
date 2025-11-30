from django.conf import settings
from shop.models import Product

import http.client
import json

class Cart:

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart
        
    def save(self):
        self.session.modified = True
        
    def add(self, product):
        product_id = str(product.id) 
        added = False
       
        if product_id not in self.cart:
            if product.inventory > 0:
                self.cart[product_id] = {
                    'quantity': 1,
                    'price': product.new_price,
                    'weight': product.weight,
                }
                added = True
        else:
            if self.cart[product_id]['quantity'] < product.inventory:
                self.cart[product_id]['quantity'] += 1
                added = True
            self.cart[product_id]['price'] = product.new_price
            self.cart[product_id]['weight'] = product.weight
        self.session['cart'] = self.cart
        self.save()
        return added
        # -------------------------------------------------


        # -------------------------------------------------
    def decrease(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            if self.cart[product_id]['quantity'] > 1:
                self.cart[product_id]['quantity'] -= 1
            else:
                del self.cart[product_id]
                self.session['cart'] = self.cart
                self.save()
                return
            self.cart[product_id]['price'] = product.new_price
            self.cart[product_id]['weight'] = product.weight
        self.session['cart'] = self.cart
        self.save()
        
    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
        self.session['cart'] = self.cart
        self.save()
        
        
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())
    
    def clear(self):
        if 'cart' in self.session:
            del self.session['cart']
        self.cart = {}
        self.save()
        
        
        
    def get_post_price(self):
        weight = sum(item['weight']*item['quantity'] for item in self.cart.values())
        if weight <= 3000:
            return 50
        elif 3000 < weight < 5000:
            return 60
        else:
            return 70
        
    # def get_total_post_price(self):
        

        
        
    def get_total_price(self):
        return sum((item['price']) * item['quantity'] for item in self.cart.values())
         
    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart_dict = {pid: item.copy() for pid, item in self.cart.items()}
        for product in products:
            product_id = str(product.id)
            if product_id in self.cart:
                self.cart[product_id]['price'] = product.new_price
                self.cart[product_id]['weight'] = product.weight
                cart_dict[product_id]['product'] = product
        self.session['cart'] = self.cart
        self.save()
        for item in cart_dict.values():
            item['total'] = item['price'] * item['quantity']
            yield item
            
            
    def get_final_price(self):
        return self.get_total_price() + self.get_post_price()

            