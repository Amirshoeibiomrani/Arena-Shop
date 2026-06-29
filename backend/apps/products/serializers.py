"""
Serializer های اپ products

📚 چرا چند تا Serializer داریم؟
🤔 سؤال: چرا برای محصول ۳ تا Serializer ساختیم؟
1. ProductListSerializer (سبک) → برای لیست محصولات
وقتی کاربر صفحه‌ی فروشگاه رو می‌بینه، ۱۲ تا محصول لود می‌شه
نیازی نیست برای هر کدوم همه تصاویر گالری و توضیحات کامل بفرستیم
پس فقط فیلدهای ضروری (عکس اصلی، قیمت، اسم) رو می‌فرستیم
نتیجه: API سریع‌تر، اینترنت کمتر مصرف می‌شه 🚀
2. ProductDetailSerializer (کامل) → برای صفحه‌ی جزئیات یک محصول
وقتی کاربر روی یه محصول کلیک می‌کنه و صفحه‌ی جزئیاتش باز می‌شه
اینجا همه چی لازمه: گالری تصاویر، توضیح کامل، اطلاعات کامل دسته و برند
3. ProductCreateUpdateSerializer → برای ساخت/ویرایش محصول
وقتی ادمین می‌خواد محصول جدید بسازه یا ویرایش کنه
فیلدهای محاسباتی (مثل final_price) رو نداره چون قابل ویرایش نیستن
این یه پرکتیس حرفه‌ای هست که هر developer باتجربه استفاده می‌کنه. 🎯

"""

from rest_framework import serializers
from .models import Category, Brand, Product, ProductImage


# ============================================
# 1. Serializer دسته‌بندی
# ============================================
"""SerializerMethodField
وقتی می‌خوای یه فیلد سفارشی برگردونی که تو مدل نیست:
"""
class CategorySerializer(serializers.ModelSerializer):
    """نمایش دسته‌بندی به همراه تعداد محصولاتش"""
    products_count = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            'id', 'name', 'slug', 'parent', 'image',
            'description', 'is_active', 'products_count', 'children',
        )

    def get_products_count(self, obj):
        """تعداد محصولات این دسته"""
        return obj.products.filter(status='published').count()

    def get_children(self, obj):
        """دسته‌های فرزند (فقط اسم و slug)"""
        children = obj.children.filter(is_active=True)
        return [{'id': c.id, 'name': c.name, 'slug': c.slug} for c in children]


# ============================================
# 2. Serializer برند
# ============================================
class BrandSerializer(serializers.ModelSerializer):
    """نمایش برند به همراه تعداد محصولاتش"""

    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = (
            'id', 'name', 'slug', 'logo',
            'description', 'is_active', 'products_count',
        )

    def get_products_count(self, obj):
        return obj.products.filter(status='published').count()


# ============================================
# 3. Serializer تصویر محصول
# ============================================
class ProductImageSerializer(serializers.ModelSerializer):
    """تصاویر گالری محصول"""

    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text', 'order')


# ============================================
# 4. Serializer لیست محصولات (سبک - برای صفحه لیست)
# ============================================
class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializer سبک برای نمایش در لیست محصولات
    فقط فیلدهای ضروری رو شامل می‌شه (سرعت بالاتر)
    """
# source='category.name'
# به جای اینکه کل اطلاعات دسته رو برگردونی، فقط اسمش رو می‌خوای:
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    final_price = serializers.IntegerField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    class Meta:
        model = Product
        fields = (
            'id', 'title', 'slug', 'main_image',
            'category_name', 'brand_name',
            'price', 'discount_price', 'final_price', 'discount_percentage',
            'stock', 'is_in_stock', 'is_featured', 'status',
        )


# ============================================
# 5. Serializer جزئیات محصول (کامل)
# ============================================
class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializer کامل برای صفحه جزئیات محصول
    شامل: تصاویر گالری، دسته‌بندی کامل، برند کامل
    """

    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    # many=True
# وقتی یه رابطه چند به یک داری (یه محصول چند تصویر):
    final_price = serializers.IntegerField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'title', 'slug',
            'category', 'brand',
            'short_description', 'description',
            'main_image', 'images',
            'price', 'discount_price', 'final_price', 'discount_percentage',
            'stock', 'is_in_stock',
            'status', 'is_featured',
            'views_count', 'sold_count',
            'created_at', 'updated_at',
        )


# ============================================
# 6. Serializer ایجاد/ویرایش محصول (برای ادمین)
# ============================================
class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer برای ساخت و ویرایش محصول"""

    class Meta:
        model = Product
        fields = (
            'title', 'slug', 'category', 'brand',
            'short_description', 'description',
            'main_image', 'price', 'discount_price', 'stock',
            'status', 'is_featured',
        )

    def validate(self, attrs):
        """اعتبارسنجی: قیمت تخفیف باید کمتر از قیمت اصلی باشه"""
        price = attrs.get('price')
        discount_price = attrs.get('discount_price')
        if discount_price and price and discount_price >= price:
            raise serializers.ValidationError({
                'discount_price': 'قیمت تخفیف باید کمتر از قیمت اصلی باشد.'
            })
        return attrs