"""
Serializer های داشبورد ادمین
"""
from rest_framework import serializers


# ============================================
# Serializer آمار کلی
# ============================================
class OverviewStatsSerializer(serializers.Serializer):
    """آمار کلی داشبورد"""

    total_revenue = serializers.IntegerField(label='کل درآمد')
    total_orders = serializers.IntegerField(label='تعداد سفارش‌ها')
    total_products = serializers.IntegerField(label='تعداد محصولات')
    total_users = serializers.IntegerField(label='تعداد کاربران')

    # رشد نسبت به ماه قبل
    revenue_growth = serializers.FloatField(label='رشد درآمد (%)')
    orders_growth = serializers.FloatField(label='رشد سفارش‌ها (%)')

    # آمار سفارش‌ها بر اساس وضعیت
    pending_orders = serializers.IntegerField(label='در انتظار')
    processing_orders = serializers.IntegerField(label='در حال آماده‌سازی')
    delivered_orders = serializers.IntegerField(label='تحویل داده شده')


# ============================================
# Serializer نمودار فروش روزانه
# ============================================
class DailySalesSerializer(serializers.Serializer):
    """آمار فروش روزانه برای نمودار خطی"""
    date = serializers.DateField()
    total_sales = serializers.IntegerField()
    orders_count = serializers.IntegerField()


# ============================================
# Serializer پرفروش‌ترین محصولات
# ============================================
class TopProductSerializer(serializers.Serializer):
    """محصولات پرفروش"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    main_image = serializers.ImageField(allow_null=True)
    price = serializers.IntegerField()
    sold_count = serializers.IntegerField()
    total_revenue = serializers.IntegerField()


# ============================================
# Serializer جدیدترین سفارش‌ها
# ============================================
class RecentOrderSerializer(serializers.Serializer):
    """آخرین سفارش‌ها برای نمایش در داشبورد"""
    id = serializers.IntegerField()
    order_number = serializers.CharField()
    user_email = serializers.CharField()
    user_full_name = serializers.CharField()
    status = serializers.CharField()
    status_display = serializers.CharField()
    total_price = serializers.IntegerField()
    items_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()


# ============================================
# Serializer سفارش‌ها بر اساس وضعیت
# ============================================
class OrdersByStatusSerializer(serializers.Serializer):
    """برای Pie Chart - تعداد سفارش‌ها در هر وضعیت"""
    status = serializers.CharField()
    status_display = serializers.CharField()
    count = serializers.IntegerField()


# ============================================
# Serializer کاربران اخیر
# ============================================
class RecentUserSerializer(serializers.Serializer):
    """کاربران تازه ثبت‌نام شده"""
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.CharField()
    full_name = serializers.CharField()
    avatar = serializers.ImageField(allow_null=True)
    orders_count = serializers.IntegerField()
    date_joined = serializers.DateTimeField()

    """📚 توضیح: چرا اینبار از serializers.Serializer استفاده کردیم نه ModelSerializer؟
داشبورد داده‌های محاسباتی و ترکیبی برمی‌گردونه نه یه مدل خاص. مثلاً:

"کل درآمد" یه عدد محاسبه شده‌ست، نه فیلد یه مدل
"رشد نسبت به ماه قبل" از مقایسه دو دوره میاد
"پرفروش‌ترین‌ها" نیاز به annotate و aggregate داره
پس از Serializer ساده استفاده می‌کنیم و دستی فیلدها رو تعریف می‌کنیم."""