"""
مدل‌های سبد خرید و سفارش‌ها
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.products.models import Product


# ============================================
# 1. سبد خرید
# ============================================
class Cart(models.Model):
    """
    سبد خرید کاربر - هر کاربر یک سبد خرید فعال داره
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name='کاربر',
        on_delete=models.CASCADE,
        related_name='cart',
    )
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین تغییر', auto_now=True)

    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبدهای خرید'

    def __str__(self):
        return f"سبد {self.user.email}"

    @property
    def total_items(self):
        """تعداد کل آیتم‌ها (با احتساب quantity)"""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        """مبلغ کل سبد خرید"""
        return sum(item.subtotal for item in self.items.all())


# ============================================
# 2. آیتم سبد خرید
# ============================================
class CartItem(models.Model):
    """هر محصولی که تو سبد خرید قرار می‌گیره"""

    cart = models.ForeignKey(
        Cart,
        verbose_name='سبد خرید',
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        Product,
        verbose_name='محصول',
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(
        'تعداد',
        default=1,
        validators=[MinValueValidator(1)],
    )
    added_at = models.DateTimeField('تاریخ افزودن', auto_now_add=True)

    class Meta:
        verbose_name = 'آیتم سبد'
        verbose_name_plural = 'آیتم‌های سبد'
        unique_together = ('cart', 'product')  # هر محصول فقط یک بار در سبد

    def __str__(self):
        return f"{self.product.title} × {self.quantity}"

    @property
    def unit_price(self):
        """قیمت واحد (با احتساب تخفیف)"""
        return self.product.final_price

    @property
    def subtotal(self):
        """مبلغ کل این آیتم"""
        return self.unit_price * self.quantity


# ============================================
# 3. سفارش
# ============================================
class Order(models.Model):
    """سفارش نهایی شده"""

    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('processing', 'در حال آماده‌سازی'),
        ('shipped', 'ارسال شده'),
        ('delivered', 'تحویل داده شده'),
        ('cancelled', 'لغو شده'),
    ]

    # کاربر سفارش‌دهنده
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='کاربر',
        on_delete=models.PROTECT,  # نذار کاربری که سفارش داره پاک بشه
        related_name='orders',
    )

    # شماره پیگیری یکتا
    order_number = models.CharField('شماره سفارش', max_length=20, unique=True, blank=True)

    # وضعیت
    status = models.CharField(
        'وضعیت',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )

    # اطلاعات گیرنده (snapshot - حتی اگه کاربر آدرسش رو تغییر بده، سفارش قدیمی همینه)
    receiver_name = models.CharField('نام گیرنده', max_length=200)
    receiver_phone = models.CharField('تلفن گیرنده', max_length=11)
    shipping_address = models.TextField('آدرس ارسال')
    postal_code = models.CharField('کد پستی', max_length=10)

    # قیمت‌گذاری
    items_total = models.DecimalField(
        'جمع آیتم‌ها',
        max_digits=12,
        decimal_places=0,
        default=0,
    )
    shipping_cost = models.DecimalField(
        'هزینه ارسال',
        max_digits=10,
        decimal_places=0,
        default=50000,  # پیش‌فرض ۵۰ هزار تومان
    )
    total_price = models.DecimalField(
        'مبلغ کل',
        max_digits=12,
        decimal_places=0,
        default=0,
    )

    # توضیحات
    note = models.TextField('توضیحات سفارش', blank=True)

    # تاریخ‌ها
    created_at = models.DateTimeField('تاریخ ثبت', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین تغییر', auto_now=True)
    paid_at = models.DateTimeField('تاریخ پرداخت', blank=True, null=True)
    delivered_at = models.DateTimeField('تاریخ تحویل', blank=True, null=True)

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f"سفارش {self.order_number} - {self.user.email}"

    def save(self, *args, **kwargs):
        # اگه شماره سفارش نداره، بسازش
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_order_number():
        """ساخت شماره سفارش یکتا مثل: ORD-20260605-A1B2"""
        import random
        import string
        from django.utils import timezone

        date_part = timezone.now().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"ORD-{date_part}-{random_part}"

    def calculate_total(self):
        """محاسبه و آپدیت قیمت کل"""
        self.items_total = sum(item.subtotal for item in self.items.all())
        self.total_price = self.items_total + self.shipping_cost
        self.save(update_fields=['items_total', 'total_price'])


# ============================================
# 4. آیتم سفارش
# ============================================
class OrderItem(models.Model):
    """
    آیتم‌های هر سفارش
    قیمت رو ذخیره می‌کنیم تا با تغییر قیمت محصول، سفارش قدیمی تغییر نکنه
    """
    order = models.ForeignKey(
        Order,
        verbose_name='سفارش',
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        Product,
        verbose_name='محصول',
        on_delete=models.PROTECT,
    )
    product_title = models.CharField('عنوان محصول', max_length=200)  # snapshot
    unit_price = models.DecimalField(
        'قیمت واحد',
        max_digits=12,
        decimal_places=0,
    )
    quantity = models.PositiveIntegerField('تعداد')

    class Meta:
        verbose_name = 'آیتم سفارش'
        verbose_name_plural = 'آیتم‌های سفارش'

    def __str__(self):
        return f"{self.product_title} × {self.quantity}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    """📚 توضیح مدل‌ها (نکات مهم!)
🔹 OneToOneField تو Cart
هر کاربر فقط یک سبد خرید فعال داره. اگه از ForeignKey استفاده می‌کردیم، یه کاربر می‌تونست چند سبد داشته باشه که منطقی نیست.

🔹 unique_together = ('cart', 'product')
نمی‌ذاره یه محصول دو بار تو سبد قرار بگیره. اگه دوبار اضافه کنی، quantity رو زیاد می‌کنیم نه ایتم جدید.

🔹 on_delete=models.PROTECT تو Order
اگه کاربری سفارش داره، نمی‌ذاریم پاک بشه. این یه پرکتیس مهم تجارت الکترونیکه چون باید سابقه فروش حفظ بشه.

🔹 چرا تو OrderItem فیلدهای product_title و unit_price تکراری داریم؟
این بزرگ‌ترین درس این بخشه! 🎯

سناریو: فرض کن یه نفر گوشی رو ۵۰ میلیون می‌خره. شش ماه بعد، شما اسم محصول رو تغییر می‌دی و قیمت رو می‌کنی ۶۰ میلیون.

اگه فیلد product_title و unit_price نداشتیم: فاکتور قدیمی، اسم و قیمت جدید رو نشون می‌داد! ❌
ولی الان: فاکتور قدیمی همون اطلاعات لحظه خرید رو حفظ می‌کنه ✅
این مفهوم به اسم Snapshot Pattern معروفه.

🔹 generate_order_number()
شماره سفارش زیبا مثل ORD-20260605-A1B2. به جای ID عددی ساده، این برای مشتری حرفه‌ای‌تره.
"""