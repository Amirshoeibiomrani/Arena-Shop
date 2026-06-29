"""
مدل‌های محصولات فروشگاه
شامل: دسته‌بندی، برند، محصول، تصاویر محصول
"""
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator


# ============================================
# 1. دسته‌بندی (با ساختار درختی)
# ============================================
class Category(models.Model):
    """
    دسته‌بندی محصولات - ساختار درختی (پدر و فرزند)
    مثال: الکترونیک > موبایل > سامسونگ
    """
    name = models.CharField('نام دسته', max_length=100)
    slug = models.SlugField('اسلاگ', max_length=120, unique=True, allow_unicode=True)
    parent = models.ForeignKey(
        'self',
        verbose_name='دسته والد',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
    )
    image = models.ImageField(
        'تصویر',
        upload_to='categories/',
        blank=True,
        null=True,
    )
    description = models.TextField('توضیحات', blank=True)
    is_active = models.BooleanField('فعال', default=True)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'
        ordering = ['name']

    def __str__(self):
        # اگه دسته والد داشته باشه، اسمشو هم نشون بده
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        # اگه slug نداده شده، خودکار از روی اسم بساز
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


# ============================================
# 2. برند
# ============================================
class Brand(models.Model):
    """برند یا تولیدکننده محصول"""

    name = models.CharField('نام برند', max_length=100, unique=True)
    slug = models.SlugField('اسلاگ', max_length=120, unique=True, allow_unicode=True)
    logo = models.ImageField('لوگو', upload_to='brands/', blank=True, null=True)
    description = models.TextField('توضیحات', blank=True)
    is_active = models.BooleanField('فعال', default=True)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)

    class Meta:
        verbose_name = 'برند'
        verbose_name_plural = 'برندها'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


# ============================================
# 3. محصول
# ============================================
class Product(models.Model):
    """محصول اصلی فروشگاه"""

    STATUS_CHOICES = [
        ('draft', 'پیش‌نویس'),
        ('published', 'منتشر شده'),
        ('out_of_stock', 'ناموجود'),
    ]

    # اطلاعات اصلی
    title = models.CharField('عنوان', max_length=200)
    slug = models.SlugField('اسلاگ', max_length=220, unique=True, allow_unicode=True)
    category = models.ForeignKey(
        Category,
        verbose_name='دسته‌بندی',
        on_delete=models.PROTECT,
        related_name='products',
    )
    brand = models.ForeignKey(
        Brand,
        verbose_name='برند',
        on_delete=models.SET_NULL,
        related_name='products',
        blank=True,
        null=True,
    )

    # توضیحات
    short_description = models.CharField('توضیح کوتاه', max_length=300, blank=True)
    description = models.TextField('توضیح کامل')

    # قیمت‌گذاری
    price = models.DecimalField(
        'قیمت (تومان)',
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(0)],
    )
    discount_price = models.DecimalField(
        'قیمت با تخفیف (تومان)',
        max_digits=12,
        decimal_places=0,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )

    # موجودی
    stock = models.PositiveIntegerField('موجودی', default=0)

    # تصویر اصلی
    main_image = models.ImageField(
        'تصویر اصلی',
        upload_to='products/main/',
        blank=True,
        null=True,
    )

    # وضعیت
    status = models.CharField(
        'وضعیت',
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
    )
    is_featured = models.BooleanField('محصول ویژه', default=False)

    # آمار
    views_count = models.PositiveIntegerField('تعداد بازدید', default=0)
    sold_count = models.PositiveIntegerField('تعداد فروش', default=0)

    # تاریخ‌ها
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('تاریخ بروزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status', 'is_featured']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    @property
    def final_price(self):
        """قیمت نهایی - اگه تخفیف داره، قیمت تخفیف رو برگردون"""
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percentage(self):
        """درصد تخفیف"""
        if self.discount_price and self.price > 0:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

    @property
    def is_in_stock(self):
        """آیا موجوده؟"""
        return self.stock > 0 and self.status == 'published'


# ============================================
# 4. تصاویر محصول (گالری)
# ============================================
class ProductImage(models.Model):
    """تصاویر اضافی محصول (گالری)"""

    product = models.ForeignKey(
        Product,
        verbose_name='محصول',
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField('تصویر', upload_to='products/gallery/')
    alt_text = models.CharField('متن جایگزین', max_length=200, blank=True)
    order = models.PositiveIntegerField('ترتیب نمایش', default=0)

    class Meta:
        verbose_name = 'تصویر محصول'
        verbose_name_plural = 'تصاویر محصولات'
        ordering = ['order']

    def __str__(self):
        return f"تصویر {self.product.title}"


    """📚 توضیح مدل‌ها
🔹 Category (دسته‌بندی درختی)
parent = ForeignKey('self', ...) → خود‌ارجاع! یعنی یه دسته می‌تونه والد یه دسته دیگه باشه
مثلاً: الکترونیک → موبایل → سامسونگ
related_name='children' → از طریق category.children.all() به فرزندانش دسترسی داری
🔹 SlugField چیه؟
URL دوستانه! مثلاً به جای /products/123/، می‌شه /products/گوشی-سامسونگ-s25/
allow_unicode=True یعنی فارسی هم قبول می‌کنه.

🔹 متد save() سفارشی
اگه slug ندادیم، خودکار از روی اسم می‌سازه. خیلی راحت!

🔹 on_delete چیه؟
وقتی یه دسته یا برند پاک می‌شه، با محصولاتش چی کنیم؟

CASCADE → محصولات هم پاک بشن (خطرناک!)
PROTECT → نذار دسته‌ای که محصول داره پاک بشه (امن - برای دسته‌بندی)
SET_NULL → فقط مقدارش رو null کن (برای برند مناسبه)
🔹 @property final_price
این یه فیلد محاسباتیه. هر جا بنویسی product.final_price، خودش بررسی می‌کنه قیمت تخفیف داره یا نه.

🔹 indexes
ایندکس‌های دیتابیس برای جستجوی سریع‌تر. وقتی محصولات زیاد بشن، این فرق بزرگی می‌سازه!

🔹 ProductImage
یه محصول می‌تونه چند تصویر داشته باشه (گالری).

related_name='images' → از طریق product.images.all() به همه تصاویرش دسترسی داری
"""