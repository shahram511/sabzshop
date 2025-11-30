from django.db.models.signals import pre_save
from django.dispatch import receiver

from order.sms import send_sms
from .models import Order, OrderItem, Transaction
from django.http import HttpResponse

@receiver(pre_save, sender=Order)
def update_order_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_order = Order.objects.get(pk=instance.pk)
            old_status = old_order.order_status
            
            new_status = instance.order_status
            
            if old_status != new_status:
                
                status_message = {
                    'pending': 'Order is pending',
                    'confirmed': 'Order is confirmed',
                    'shipped': 'Order is shipped',
                    'delivered': 'Order is delivered',
                    'cancelled': 'Order is cancelled',
                    'returned': 'Order is returned',
                }
                message = f'Order {instance.id} status changed to {status_message[new_status]}'
                
                if instance.buyer and instance.buyer.phone:
                    try:
                        # send_sms(instance.buyer.phone, message)
                        print(f'SMS sent to {instance.buyer.phone}: {message}')
                    except Exception as e:
                        print(f'Error sending SMS: {e}')
                        
        except Order.DoesNotExist:
            print(f'Order {instance.id} does not exist')
            pass

@receiver(pre_save, sender=Order)
def create_transaction_on_payment(sender, instance, **kwargs):
    """
    Automatically create Transaction when order.paid changes from False to True
    """
    if instance.pk:  # Only for existing orders
        try:
            old_order = Order.objects.get(pk=instance.pk)
            # Check if paid status changed from False to True
            if not old_order.paid and instance.paid:
                # Check if transaction already exists for this order
                if not Transaction.objects.filter(order=instance, status='success').exists():
                    # Create transaction automatically
                    Transaction.objects.create(
                        order=instance,
                        amount=instance.get_total_price_with_post(),
                        status='success',
                    )
                    print(f'Transaction created automatically for Order {instance.id}')
        except Order.DoesNotExist:
            pass