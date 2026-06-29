"""
URL های اپ orders
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CartView,
    CartAddView,
    CartItemUpdateView,
    CartClearView,
    OrderViewSet,
)

router = DefaultRouter()
router.register('orders', OrderViewSet, basename='order')

urlpatterns = [
    # سبد خرید
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', CartAddView.as_view(), name='cart-add'),
    path('cart/items/<int:pk>/', CartItemUpdateView.as_view(), name='cart-item-update'),
    path('cart/clear/', CartClearView.as_view(), name='cart-clear'),

    # سفارش‌ها (با Router)
    path('', include(router.urls)),
]