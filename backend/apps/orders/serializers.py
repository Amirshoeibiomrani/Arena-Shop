"""
Serializer های سبد خرید و سفارش‌ها
"""
from rest_framework import serializers
from django.db import transaction

from apps.products.models import Product
from apps.products.serializers import ProductListSerializer
from .models import Cart, CartItem, Order, OrderItem


# ============================================
# Serializer های سبد خرید
# ============================================
class CartItemSerializer(serializers.ModelSerializer):
    """نمایش آیتم سبد خرید"""
    product = ProductListSerializer(read_only=True)
    unit_price = serializers.IntegerField(read_only=True)
    subtotal = serializers.IntegerField(read_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'quantity', 'unit_price', 'subtotal', 'added_at')


class CartItemAddSerializer(serializers.Serializer):
    """اضافه کردن محصول به سبد"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value, status='published')
        except Product.DoesNotExist:
            raise serializers.ValidationError('محصول یافت نشد یا منتشر نشده.')
        self.context['product'] = product
        return value

    def validate(self, attrs):
        product = self.context.get('product')
        if product and attrs['quantity'] > product.stock:
            raise serializers.ValidationError({
                'quantity': f'موجودی کافی نیست. (موجودی: {product.stock})'
            })
        return attrs


class CartItemUpdateSerializer(serializers.Serializer):
    """به‌روزرسانی تعداد یک آیتم"""
    quantity = serializers.IntegerField(min_value=1)


class CartSerializer(serializers.ModelSerializer):
    """نمایش کامل سبد خرید"""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_items', 'total_price', 'updated_at')


# ============================================
# Serializer های سفارش
# ============================================
class OrderItemSerializer(serializers.ModelSerializer):
    """نمایش آیتم سفارش"""
    subtotal = serializers.IntegerField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_title', 'unit_price', 'quantity', 'subtotal')


class OrderListSerializer(serializers.ModelSerializer):
    """لیست سفارش‌ها (سبک)"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'status', 'status_display',
            'total_price', 'items_count', 'created_at',
        )

    def get_items_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """جزئیات کامل سفارش"""
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'user_email', 'status', 'status_display',
            'receiver_name', 'receiver_phone', 'shipping_address', 'postal_code',
            'items', 'items_total', 'shipping_cost', 'total_price',
            'note', 'created_at', 'paid_at', 'delivered_at',
        )


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    ساخت سفارش از روی سبد خرید
    منطق: همه آیتم‌های سبد رو به OrderItem تبدیل می‌کنه، موجودی محصول رو کم می‌کنه و سبد رو خالی می‌کنه
    """
    class Meta:
        model = Order
        fields = (
            'receiver_name', 'receiver_phone',
            'shipping_address', 'postal_code', 'note',
        )

    def validate(self, attrs):
        """چک می‌کنه که سبد خرید کاربر خالی نباشه"""
        user = self.context['request'].user
        try:
            cart = user.cart
        except Cart.DoesNotExist:
            raise serializers.ValidationError('سبد خرید شما خالی است.')

        if not cart.items.exists():
            raise serializers.ValidationError('سبد خرید شما خالی است.')

        # چک کن موجودی همه محصولات کافیه
        for item in cart.items.all():
            if item.quantity > item.product.stock:
                raise serializers.ValidationError(
                    f'موجودی محصول "{item.product.title}" کافی نیست.'
                )

        self.context['cart'] = cart
        return attrs

    @transaction.atomic  # تراکنش - یا همه با هم انجام شه یا هیچکدوم
    def create(self, validated_data):
        user = self.context['request'].user
        cart = self.context['cart']

        # ساخت سفارش
        order = Order.objects.create(user=user, **validated_data)

        # تبدیل آیتم‌های سبد به آیتم‌های سفارش
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_title=cart_item.product.title,  # snapshot
                unit_price=cart_item.product.final_price,
                quantity=cart_item.quantity,
            )
            # کاهش موجودی محصول
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.sold_count += cart_item.quantity
            cart_item.product.save(update_fields=['stock', 'sold_count'])

        # محاسبه قیمت کل
        order.calculate_total()

        # خالی کردن سبد
        cart.items.all().delete()

        return order


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """فقط برای ادمین - تغییر وضعیت سفارش"""
    class Meta:
        model = Order
        fields = ('status',)


        """📚 نکات مهم Serializer ها
🔥 @transaction.atomic
این یه دکوریتور حیاتی برای کارهای مهمه! یعنی:

"همه عملیات داخل این تابع رو با هم انجام بده. اگه یه جا خطا داد، همه رو undo کن."

تصور کن:

سفارش ساخته شد ✅
آیتم اول رفت تو سفارش ✅
آیتم دوم رفت ✅
موقع کم کردن موجودی، خطا داد ❌
بدون transaction.atomic، سفارش با ۲ آیتم می‌مونه ولی ناقصه! با transaction.atomic، همه چی undo می‌شه انگار هیچ اتفاقی نیفتاده. 🎯

🔹 منطق OrderCreateSerializer.create()
این مهم‌ترین متد این فایله:

سفارش جدید می‌سازه
هر آیتم سبد رو به OrderItem تبدیل می‌کنه (با snapshot قیمت)
موجودی محصول رو کم می‌کنه
آمار فروش محصول رو زیاد می‌کنه
قیمت کل رو محاسبه می‌کنه
سبد خرید رو خالی می‌کنه"""
