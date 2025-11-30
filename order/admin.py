from django.contrib import admin
from .models import Order, OrderItem, Transaction, DiscountCode
from django.http import HttpResponse
try:
    import openpyxl
except ImportError:
    openpyxl = None
  
import csv    
# Register your models here.


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ['product']
    
def export_to_csv(self, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Phone', 'First Name', 'Last Name', 'Email', 'City', 'Province', 'Address', 'Postal Code', 'Created', 'Paid'])
    for o in queryset:
        writer.writerow([o.id, o.phone, o.first_name, o.last_name, o.email, o.city, o.province, o.address, o.postal_code, o.created, o.paid])
    return response
    
export_to_csv.short_description = 'Export to CSV'
# ----------------------------------------------------
def export_to_excel(self, request, queryset):
    
    if openpyxl is None:
        return HttpResponse('openpyxl is not installed', status=500)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="orders.xlsx"'

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Orders'
    worksheet.append(['ID', 'Phone', 'First Name', 'Last Name', 'Email', 'City', 'Province', 'Address', 'Postal Code', 'Created', 'Paid'])

    for o in queryset:
        created = o.created.replace(tzinfo=None) if o.created else ''
        worksheet.append([
            o.id,
            
            o.phone or '',
            o.first_name or '',
            o.last_name or '',
            o.email or '',
            o.city or '',
            o.province or '',
            o.address or '',
            o.postal_code or '',
            created,
            bool(o.paid),
        ])
    workbook.save(response)
    return response

export_to_excel.short_description = 'Export to Excel'    
# ----------------------------------------------------
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'phone', 'first_name', 'last_name', 'email', 'order_status', 'city', 'province', 'address', 'postal_code', 'created', 'updated', 'paid']
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]
    actions = [export_to_excel, export_to_csv]
    list_editable = ['order_status']
    
        
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'price', 'quantity', 'weight']
    list_filter = ['order', 'product']
    search_fields = ['order', 'product']
    raw_id_fields = ['order', 'product']
    
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'status', 'created']
    list_filter = ['order', 'status', 'created']
    search_fields = ['order', 'status']
    raw_id_fields = ['order']

@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'discount_amount', 'min_purchase', 'max_discount', 'is_active', 'valid_from', 'valid_to', 'usage_limit', 'used_count']
    list_filter = ['is_active', 'valid_from', 'valid_to']
    search_fields = ['code']
    readonly_fields = ['used_count']
    
    