"""
URL های اپ products با استفاده از Router
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, BrandViewSet, ProductViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('brands', BrandViewSet, basename='brand')
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]


"""📚 جادوی Router
با فقط ۳ خط (router.register(...))، این URL ها به طور خودکار ساخته می‌شن:

متد	آدرس	کار
GET	/api/v1/products/products/	لیست محصولات
POST	/api/v1/products/products/	ساخت محصول جدید
GET	/api/v1/products/products/{slug}/	جزئیات یه محصول
PUT/PATCH	/api/v1/products/products/{slug}/	ویرایش
DELETE	/api/v1/products/products/{slug}/	حذف
GET	/api/v1/products/products/featured/	محصولات ویژه
GET	/api/v1/products/products/best_sellers/	پرفروش‌ها
GET	/api/v1/products/products/discounted/	تخفیف‌دارها
تصور کن می‌خواستی همه این URL ها رو دستی بنویسی! 😱

"""