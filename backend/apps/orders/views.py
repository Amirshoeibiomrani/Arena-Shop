
# سبد خرید، سفارش‌ها، پرداخت

"""
View های سبد خرید و سفارش‌ها
"""
from rest_framework import generics, status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem, Order
from .serializers import (
    CartSerializer,
    CartItemAddSerializer,
    CartItemUpdateSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    OrderCreateSerializer,
    OrderStatusUpdateSerializer,
)


# ============================================
# View های سبد خرید
# ============================================
class CartView(APIView):
    """
    مشاهده سبد خرید فعلی کاربر
    GET /api/v1/orders/cart/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)


class CartAddView(APIView):
    """
    اضافه کردن محصول به سبد
    POST /api/v1/orders/cart/add/
    body: { "product_id": 1, "quantity": 2 }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CartItemAddSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        product = serializer.context['product']
        quantity = serializer.validated_data['quantity']

        # سبد رو پیدا کن یا بساز
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # اگه محصول قبلاً تو سبد بود، تعدادش رو زیاد کن
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity},
        )
        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                return Response(
                    {'error': f'موجودی کافی نیست. (موجودی: {product.stock})'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = new_quantity
            cart_item.save()

        cart_serializer = CartSerializer(cart, context={'request': request})
        return Response({
            'message': 'محصول به سبد اضافه شد',
            'cart': cart_serializer.data,
        }, status=status.HTTP_200_OK)


class CartItemUpdateView(APIView):
    """
    تغییر تعداد یک آیتم در سبد
    PATCH /api/v1/orders/cart/items/{id}/
    body: { "quantity": 3 }
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        serializer = CartItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_quantity = serializer.validated_data['quantity']
        if new_quantity > cart_item.product.stock:
            return Response(
                {'error': f'موجودی کافی نیست. (موجودی: {cart_item.product.stock})'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = new_quantity
        cart_item.save()

        cart_serializer = CartSerializer(cart_item.cart, context={'request': request})
        return Response(cart_serializer.data)

    def delete(self, request, pk):
        """حذف یک آیتم از سبد"""
        cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        cart = cart_item.cart
        cart_item.delete()
        cart_serializer = CartSerializer(cart, context={'request': request})
        return Response(cart_serializer.data)


class CartClearView(APIView):
    """
    خالی کردن کامل سبد
    DELETE /api/v1/orders/cart/clear/
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        try:
            cart = request.user.cart
            cart.items.all().delete()
            return Response({'message': 'سبد خرید خالی شد'})
        except Cart.DoesNotExist:
            return Response({'message': 'سبد خرید خالی است'})


# ============================================
# ViewSet سفارش‌ها
# ============================================
class OrderViewSet(viewsets.ModelViewSet):
    """
    مدیریت سفارش‌ها
    - GET    /api/v1/orders/orders/         لیست سفارش‌های کاربر
    - POST   /api/v1/orders/orders/         ثبت سفارش جدید (از روی سبد)
    - GET    /api/v1/orders/orders/{id}/    جزئیات سفارش
    - PATCH  /api/v1/orders/orders/{id}/change_status/  تغییر وضعیت (ادمین)
    """
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'head', 'options']  # DELETE نداریم!

    def get_queryset(self):
        """کاربر فقط سفارش‌های خودش رو می‌بینه، ادمین همه رو"""
        if self.request.user.is_staff:
            return Order.objects.all().select_related('user').prefetch_related('items')
        return Order.objects.filter(user=self.request.user).prefetch_related('items')

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'create':
            return OrderCreateSerializer
        elif self.action == 'change_status':
            return OrderStatusUpdateSerializer
        return OrderDetailSerializer

    def create(self, request, *args, **kwargs):
        """ثبت سفارش جدید از روی سبد خرید"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        # بعد از ساخت، جزئیات کامل سفارش رو برگردون
        detail_serializer = OrderDetailSerializer(order, context={'request': request})
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def change_status(self, request, pk=None):
        """تغییر وضعیت سفارش (فقط ادمین)"""
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # اگه وضعیت به paid تغییر کرد، تاریخ پرداخت رو ست کن
        from django.utils import timezone
        new_status = serializer.validated_data.get('status')
        if new_status == 'paid' and not order.paid_at:
            order.paid_at = timezone.now()
            order.save(update_fields=['paid_at'])
        elif new_status == 'delivered' and not order.delivered_at:
            order.delivered_at = timezone.now()
            order.save(update_fields=['delivered_at'])

        detail_serializer = OrderDetailSerializer(order, context={'request': request})
        return Response(detail_serializer.data)