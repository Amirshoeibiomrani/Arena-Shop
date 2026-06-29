
# API های آماری برای داشبورد ادمین

"""
View های داشبورد ادمین
از Aggregation و Annotation Django استفاده می‌کنیم
"""
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.products.models import Product
from apps.orders.models import Order, OrderItem

from .permissions import IsStaffUser
from .serializers import (
    OverviewStatsSerializer,
    DailySalesSerializer,
    TopProductSerializer,
    RecentOrderSerializer,
    OrdersByStatusSerializer,
    RecentUserSerializer,
)

User = get_user_model()


# ============================================
# Helper برای محاسبه درصد رشد
# ============================================
def calculate_growth(current, previous):
    """درصد رشد بین دو عدد"""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100, 1)


# ============================================
# 1. آمار کلی (Overview Stats)
# ============================================
class OverviewStatsView(APIView):
    """
    آمار کلی داشبورد
    GET /api/v1/dashboard/overview/
    """
    permission_classes = [IsStaffUser]

    def get(self, request):
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        sixty_days_ago = now - timedelta(days=60)

        # سفارش‌هایی که "پرداخت شده" به بعد هستن (فروش واقعی)
        paid_statuses = ['paid', 'processing', 'shipped', 'delivered']
        paid_orders = Order.objects.filter(status__in=paid_statuses)

        # ===== کل درآمد =====
        total_revenue = paid_orders.aggregate(
            total=Sum('total_price')
        )['total'] or 0

        # ===== درآمد ۳۰ روز اخیر =====
        revenue_last_30 = paid_orders.filter(
            created_at__gte=thirty_days_ago
        ).aggregate(total=Sum('total_price'))['total'] or 0

        # ===== درآمد ۳۰ روز قبل از اون =====
        revenue_previous_30 = paid_orders.filter(
            created_at__gte=sixty_days_ago,
            created_at__lt=thirty_days_ago,
        ).aggregate(total=Sum('total_price'))['total'] or 0

        # ===== رشد درآمد =====
        revenue_growth = calculate_growth(revenue_last_30, revenue_previous_30)

        # ===== تعداد سفارش‌ها =====
        total_orders = Order.objects.count()

        orders_last_30 = Order.objects.filter(created_at__gte=thirty_days_ago).count()
        orders_previous_30 = Order.objects.filter(
            created_at__gte=sixty_days_ago,
            created_at__lt=thirty_days_ago,
        ).count()
        orders_growth = calculate_growth(orders_last_30, orders_previous_30)

        # ===== سایر آمارها =====
        total_products = Product.objects.filter(status='published').count()
        total_users = User.objects.filter(is_staff=False).count()

        # ===== سفارش‌ها بر اساس وضعیت =====
        pending_orders = Order.objects.filter(status='pending').count()
        processing_orders = Order.objects.filter(status='processing').count()
        delivered_orders = Order.objects.filter(status='delivered').count()

        data = {
            'total_revenue': int(total_revenue),
            'total_orders': total_orders,
            'total_products': total_products,
            'total_users': total_users,
            'revenue_growth': revenue_growth,
            'orders_growth': orders_growth,
            'pending_orders': pending_orders,
            'processing_orders': processing_orders,
            'delivered_orders': delivered_orders,
        }

        serializer = OverviewStatsSerializer(data)
        return Response(serializer.data)


# ============================================
# 2. نمودار فروش روزانه
# ============================================
class DailySalesView(APIView):
    """
    آمار فروش روزانه برای نمودار
    GET /api/v1/dashboard/daily-sales/?days=30
    """
    permission_classes = [IsStaffUser]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        paid_statuses = ['paid', 'processing', 'shipped', 'delivered']

        # گروه‌بندی بر اساس تاریخ روز
        daily_data = (
            Order.objects
            .filter(status__in=paid_statuses, created_at__gte=start_date)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(
                total_sales=Sum('total_price'),
                orders_count=Count('id'),
            )
            .order_by('date')
        )
        # 📅 TruncDate چیه؟
# تاریخ کامل (با ساعت) رو به فقط تاریخ (بدون ساعت) تبدیل می‌کنه. برای گروه‌بندی روزانه استفاده می‌شه:

        # تبدیل به فرمت دلخواه
        result = [
            {
                'date': item['date'],
                'total_sales': int(item['total_sales'] or 0),
                'orders_count': item['orders_count'],
            }
            for item in daily_data
        ]

        serializer = DailySalesSerializer(result, many=True)
        return Response(serializer.data)


# ============================================
# 3. پرفروش‌ترین محصولات
# ============================================
class TopProductsView(APIView):
    """
    پرفروش‌ترین محصولات
    GET /api/v1/dashboard/top-products/?limit=5
    """
    permission_classes = [IsStaffUser]

    def get(self, request):
        limit = int(request.query_params.get('limit', 5))

        # محصولات با بیشترین فروش
        top_products = (
            Product.objects
            .filter(sold_count__gt=0)
            .annotate(
                total_revenue=F('sold_count') * F('price'),
            )
            .order_by('-sold_count')[:limit]
        )
# 🔍 F() چیه؟
# F بهت اجازه می‌ده با فیلدهای دیگه دیتابیس محاسبه کنی، بدون اینکه اطلاعات رو به Python بیاری:
        result = [
            {
                'id': p.id,
                'title': p.title,
                'main_image': p.main_image,
                'price': int(p.price),
                'sold_count': p.sold_count,
                'total_revenue': int(p.total_revenue or 0),
            }
            for p in top_products
        ]

        serializer = TopProductSerializer(result, many=True, context={'request': request})
        return Response(serializer.data)


# ============================================
# 4. جدیدترین سفارش‌ها
# ============================================
class RecentOrdersView(APIView):
    """
    آخرین سفارش‌ها
    GET /api/v1/dashboard/recent-orders/?limit=10
    """
    permission_classes = [IsStaffUser]

    def get(self, request):
        limit = int(request.query_params.get('limit', 10))

        recent_orders = (
            Order.objects
            .select_related('user')
            .prefetch_related('items')
            .order_by('-created_at')[:limit]
        )

        result = []
        for order in recent_orders:
            result.append({
                'id': order.id,
                'order_number': order.order_number,
                'user_email': order.user.email,
                'user_full_name': order.user.full_name,
                'status': order.status,
                'status_display': order.get_status_display(),
                'total_price': int(order.total_price),
                'items_count': order.items.count(),
                'created_at': order.created_at,
            })

        serializer = RecentOrderSerializer(result, many=True)
        return Response(serializer.data)


# ============================================
# 5. سفارش‌ها بر اساس وضعیت (Pie Chart)
# ============================================
class OrdersByStatusView(APIView):
    """
    تعداد سفارش‌ها در هر وضعیت
    GET /api/v1/dashboard/orders-by-status/
    """
    permission_classes = [IsStaffUser]

    def get(self, request):
        # گروه‌بندی بر اساس وضعیت
        status_counts = (
            Order.objects
            .values('status')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # نگاشت کلیدها به اسم فارسی
        status_display_map = dict(Order.STATUS_CHOICES)

        result = [
            {
                'status': item['status'],
                'status_display': status_display_map.get(item['status'], item['status']),
                'count': item['count'],
            }
            for item in status_counts
        ]

        serializer = OrdersByStatusSerializer(result, many=True)
        return Response(serializer.data)


# ============================================
# 6. کاربران تازه ثبت‌نام شده
# ============================================
class RecentUsersView(APIView):
    """
    کاربران اخیر
    GET /api/v1/dashboard/recent-users/?limit=10
    """
    permission_classes = [IsStaffUser]

    def get(self, request):
        limit = int(request.query_params.get('limit', 10))

        recent_users = (
            User.objects
            .filter(is_staff=False)
            .annotate(orders_count=Count('orders'))
            .order_by('-date_joined')[:limit]
        )

        result = [
            {
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'full_name': u.full_name,
                'avatar': u.avatar,
                'orders_count': u.orders_count,
                'date_joined': u.date_joined,
            }
            for u in recent_users
        ]

        serializer = RecentUserSerializer(result, many=True, context={'request': request})
        return Response(serializer.data)

        # 📌 aggregate() → یه عدد برمی‌گردونه

        # 📌 annotate() → به هر آیتم یه فیلد اضافه می‌کنه



        """
        منطق revenue_growth
این یه فرمول کسب‌و‌کاره! 📊

text

رشد = ((مقدار جدید - مقدار قبلی) / مقدار قبلی) × 100
اگه ۳۰ روز اخیر ۱۰۰ میلیون فروختی و ۳۰ روز قبلش ۸۰ میلیون:

text

رشد = ((100 - 80) / 80) × 100 = 25%
        """
