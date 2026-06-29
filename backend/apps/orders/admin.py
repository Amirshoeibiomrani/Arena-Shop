"""
پنل ادمین سفارش‌ها
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem, Order, OrderItem


# ============================================
# سبد خرید
# ============================================
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('added_at',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items_display', 'total_price_display', 'updated_at')
    search_fields = ('user__email',)
    inlines = [CartItemInline]
    readonly_fields = ('created_at', 'updated_at')

    def total_items_display(self, obj):
        return obj.total_items
    total_items_display.short_description = 'تعداد آیتم'

    def total_price_display(self, obj):
        total = f"{int(obj.total_price):,}"
        return format_html('<strong>{} تومان</strong>', total)
    total_price_display.short_description = 'مبلغ کل'


# ============================================
# سفارش
# ============================================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_title', 'unit_price', 'quantity', 'subtotal_display')
    can_delete = False

    def subtotal_display(self, obj):
        subtotal = f"{int(obj.subtotal):,}"
        return f"{subtotal} تومان"
    subtotal_display.short_description = 'جمع'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'user', 'status_colored',
        'total_price_display', 'created_at',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__email', 'receiver_name', 'receiver_phone')
    list_editable = ('status',) if False else ()  # برای امنیت بهتر، editable نیست
    readonly_fields = (
        'order_number', 'user', 'items_total', 'total_price',
        'created_at', 'updated_at', 'paid_at', 'delivered_at',
    )
    inlines = [OrderItemInline]
    list_per_page = 25

    fieldsets = (
        ('اطلاعات سفارش', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('اطلاعات گیرنده', {
            'fields': ('receiver_name', 'receiver_phone', 'shipping_address', 'postal_code')
        }),
        ('قیمت‌گذاری', {
            'fields': ('items_total', 'shipping_cost', 'total_price')
        }),
        ('سایر', {
            'fields': ('note', 'created_at', 'updated_at', 'paid_at', 'delivered_at'),
        }),
    )

    def status_colored(self, obj):
        colors = {
            'pending': '#f39c12',
            'paid': '#3498db',
            'processing': '#9b59b6',
            'shipped': '#16a085',
            'delivered': '#27ae60',
            'cancelled': '#e74c3c',
        }
        color = colors.get(obj.status, '#7f8c8d')
        return format_html(
            '<span style="color:white;background:{};padding:4px 10px;border-radius:10px;font-size:11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_colored.short_description = 'وضعیت'

    def total_price_display(self, obj):
        total = f"{int(obj.total_price):,}"
        return format_html('<strong style="color:#27ae60;">{} تومان</strong>', total)
    total_price_display.short_description = 'مبلغ کل'