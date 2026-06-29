"""
URL های داشبورد ادمین
"""
from django.urls import path

from .views import (
    OverviewStatsView,
    DailySalesView,
    TopProductsView,
    RecentOrdersView,
    OrdersByStatusView,
    RecentUsersView,
)

urlpatterns = [
    path('overview/', OverviewStatsView.as_view(), name='dashboard-overview'),
    path('daily-sales/', DailySalesView.as_view(), name='dashboard-daily-sales'),
    path('top-products/', TopProductsView.as_view(), name='dashboard-top-products'),
    path('recent-orders/', RecentOrdersView.as_view(), name='dashboard-recent-orders'),
    path('orders-by-status/', OrdersByStatusView.as_view(), name='dashboard-orders-by-status'),
    path('recent-users/', RecentUsersView.as_view(), name='dashboard-recent-users'),
]