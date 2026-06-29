# محصولات، دسته‌بندی، برند، تصاویر
"""📌 گام ۳: ساخت ViewSet ها
ViewSet یه ابر‌قدرت Django REST Framework هست. به جای ۵ تا View جدا (List, Create, Retrieve, Update, Delete)، فقط یه کلاس می‌نویسی و همه کارها رو می‌کنه! 🔥
"""
"""📚 توضیح ViewSet (مهم!)
🔥 ModelViewSet چه ابرقدرتی داره؟
یه ModelViewSet به طور خودکار این ۶ تا متد رو می‌سازه:

list() → GET /products/ → لیست
create() → POST /products/ → ایجاد
retrieve() → GET /products/1/ → جزئیات
update() → PUT /products/1/ → ویرایش کامل
partial_update() → PATCH /products/1/ → ویرایش بخشی
destroy() → DELETE /products/1/ → حذف"""

"""
ViewSet های اپ products
"""
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F

from .models import Category, Brand, Product
from .serializers import (
    CategorySerializer,
    BrandSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
)
from .filters import ProductFilter


# ============================================
# Permission سفارشی
# ============================================
class IsAdminOrReadOnly(permissions.BasePermission):
    """
    فقط ادمین می‌تونه ویرایش کنه
    بقیه فقط می‌تونن بخونن
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return request.user and request.user.is_staff


# ============================================
# ViewSet دسته‌بندی
# ============================================
class CategoryViewSet(viewsets.ModelViewSet):
    """
    مدیریت کامل دسته‌بندی‌ها
    - GET    /api/v1/products/categories/        لیست
    - POST   /api/v1/products/categories/        ایجاد (ادمین)
    - GET    /api/v1/products/categories/{id}/   جزئیات
    - PUT    /api/v1/products/categories/{id}/   ویرایش (ادمین)
    - DELETE /api/v1/products/categories/{id}/   حذف (ادمین)
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'  # به جای id، با slug پیدا کن
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


# ============================================
# ViewSet برند
# ============================================
class BrandViewSet(viewsets.ModelViewSet):
    """مدیریت کامل برندها"""
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


# ============================================
# ViewSet محصولات (مهم‌ترین بخش)
# ============================================
class ProductViewSet(viewsets.ModelViewSet):
    """
    مدیریت کامل محصولات با امکانات پیشرفته:
    - فیلتر بر اساس دسته، برند، قیمت
    - جستجو در عنوان و توضیحات
    - مرتب‌سازی بر اساس قیمت، تاریخ، بازدید
    - Actions سفارشی: محصولات ویژه، پربازدیدها، تخفیف‌دارها
    """
    queryset = Product.objects.select_related('category', 'brand').prefetch_related('images')
    # ⚡ select_related و prefetch_related
# این مهم‌ترین بهینه‌سازی پروژه‌ست! بدون این، N+1 query problem داری:
# به جای ۱۰۰ کوئری برای ۱۰۰ محصول، فقط ۲ کوئری می‌زنه. خیلی سریع‌تر!
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    # فیلتر، جستجو، مرتب‌سازی
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'short_description', 'description', 'brand__name']
    ordering_fields = ['price', 'created_at', 'views_count', 'sold_count']
    ordering = ['-created_at']  # پیش‌فرض: جدیدترین اول

    def get_queryset(self):
        """
        کاربر عادی فقط محصولات منتشر شده رو می‌بینه
        ادمین همه محصولات رو می‌بینه
        """
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(status='published')
        return qs

    def get_serializer_class(self):
        """
        برای هر action، Serializer مناسب رو انتخاب کن:
        - list → ProductListSerializer (سبک)
        - retrieve → ProductDetailSerializer (کامل)
        - create/update → ProductCreateUpdateSerializer
        """
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        وقتی یه محصول رو می‌بینه، بازدید رو +1 کن
        از F() استفاده می‌کنیم تا race condition پیش نیاد
        """
        instance = self.get_object()
        # افزایش بازدید (atomic)
        Product.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # ============================================
    # Actions سفارشی
    # ============================================
# 🆕 @action (دکوریتور جادویی!)
# با این می‌تونی endpoint های سفارشی اضافه کنی:
# detail=False → یه URL مستقل (مثل /products/featured/)
# detail=True → URL مربوط به یه آیتم (مثل /products/1/related/)
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        محصولات ویژه
        GET /api/v1/products/products/featured/
        """
        queryset = self.get_queryset().filter(is_featured=True)[:8]
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def best_sellers(self, request):
        """
        پرفروش‌ترین‌ها
        GET /api/v1/products/products/best_sellers/
        """
        queryset = self.get_queryset().order_by('-sold_count')[:8]
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def discounted(self, request):
        """
        محصولات تخفیف‌دار
        GET /api/v1/products/products/discounted/
        """
        queryset = self.get_queryset().filter(discount_price__isnull=False)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)