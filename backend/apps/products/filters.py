"""📌 گام ۲: ساخت Filter ها
برای فیلترهای پیشرفته (مثل بازه قیمت، چند برند با هم و ...) یه فایل filter می‌سازیم."""

"""
فیلترهای پیشرفته برای محصولات
"""
import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """
    فیلترهای پیشرفته محصولات
    مثال‌ها:
        ?min_price=100000&max_price=500000
        ?category=mobile
        ?brand=samsung,apple
        ?in_stock=true
    """

    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    category = django_filters.CharFilter(field_name='category__slug', lookup_expr='exact')
    brand = django_filters.CharFilter(field_name='brand__slug', lookup_expr='exact')

    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    has_discount = django_filters.BooleanFilter(method='filter_has_discount')

    class Meta:
        model = Product
        fields = ['category', 'brand', 'is_featured', 'status']

    def filter_in_stock(self, queryset, name, value):
        """فقط محصولات موجود"""
        if value:
            return queryset.filter(stock__gt=0)
        return queryset

    def filter_has_discount(self, queryset, name, value):
        """فقط محصولات تخفیف‌دار"""
        if value:
            return queryset.filter(discount_price__isnull=False)
        return queryset



    """📚 توضیح:
lookup_expr
'gte' → بزرگ‌تر یا مساوی (Greater Than or Equal) - برای min_price
'lte' → کوچک‌تر یا مساوی - برای max_price
'exact' → دقیقاً مساوی
'icontains' → شامل بودن (case-insensitive)
متد سفارشی filter_in_stock
وقتی فیلتر استاندارد جواب نمی‌ده، می‌تونی منطق خودت رو بنویسی.

"""