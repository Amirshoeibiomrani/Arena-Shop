"""
ثبت مدل‌های products در پنل ادمین
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Product, ProductImage


# ============================================
# دسته‌بندی
# ============================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}  # خودکار slug رو از اسم پر کن
    list_editable = ('is_active',)


# ============================================
# برند
# ============================================
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_preview', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)

    def logo_preview(self, obj):
        """نمایش پیش‌نمایش لوگو در لیست"""
        if obj.logo:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius:5px;object-fit:cover;" />',
                obj.logo.url
            )
        return "—"
    logo_preview.short_description = 'لوگو'


# ============================================
# Inline برای تصاویر محصول
# ============================================
class ProductImageInline(admin.TabularInline):
    """نمایش تصاویر محصول داخل صفحه محصول"""
    model = ProductImage
    extra = 1  # یه فرم خالی اضافه نشون بده
    fields = ('image', 'alt_text', 'order')


# ============================================
# محصول
# ============================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'main_image_preview', 'title', 'category', 'brand',
        'price', 'final_price_display', 'stock', 'status', 'is_featured'
    )
    list_filter = ('status', 'is_featured', 'category', 'brand', 'created_at')
    search_fields = ('title', 'description', 'brand__name')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('status', 'is_featured')
    readonly_fields = ('views_count', 'sold_count', 'created_at', 'updated_at')
    inlines = [ProductImageInline]
    list_per_page = 20

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'slug', 'category', 'brand', 'main_image')
        }),
        ('توضیحات', {
            'fields': ('short_description', 'description')
        }),
        ('قیمت و موجودی', {
            'fields': ('price', 'discount_price', 'stock')
        }),
        ('وضعیت', {
            'fields': ('status', 'is_featured')
        }),
        ('آمار', {
            'fields': ('views_count', 'sold_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),  # قابل جمع شدن
        }),
    )

    def main_image_preview(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:5px;object-fit:cover;" />',
                obj.main_image.url
            )
        return "—"
    main_image_preview.short_description = 'تصویر'

    def final_price_display(self, obj):
        if obj.discount_price:
            discount = f"{int(obj.discount_price):,}"
            original = f"{int(obj.price):,}"
            return format_html(
                '<span style="color:green;font-weight:bold;">{}</span> <s style="color:#999;">{}</s>',
                discount, original
            )
        price = f"{int(obj.price):,}"
        return format_html('<strong>{}</strong>', price)
    final_price_display.short_description = 'قیمت نهایی'


"""
📚 توضیح:
قبل: format_html رو مجبور می‌کردیم خودش فرمت :, رو هم اجرا کنه که در Django 6 ممنوع شده.
بعد: اول با f-string عادی پایتون (f"{number:,}") عدد رو فرمت می‌کنیم (مثلاً 45000000 → 45,000,000)، بعد به عنوان متن ساده می‌فرستیم به format_html.
این روش هم امن‌تره (چون format_html فقط متن escape شده دریافت می‌کنه) و هم با Django 6 سازگاره.

"""



# ============================================
# ثبت ProductImage جدا (اختیاری)
# ============================================
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'order')
    list_filter = ('product',)


    """📚 توضیح ادمین حرفه‌ای
🎨 prepopulated_fields
وقتی اسم محصول رو می‌نویسی، slug خودکار از روی اسم پر می‌شه! خیلی راحت.

🖼️ logo_preview و main_image_preview
متد سفارشی که عکس رو به صورت thumbnail تو لیست نشون می‌ده. خیلی شیک می‌شه! 😎

📑 inlines = [ProductImageInline]
وقتی یه محصول رو ویرایش می‌کنی، تصاویر گالریش رو همونجا می‌بینی و می‌تونی اضافه/حذف کنی.

📋 fieldsets
صفحه ویرایش رو به بخش‌های منظم تقسیم می‌کنه. خیلی حرفه‌ای می‌شه!

✏️ list_editable
می‌تونی مستقیم تو لیست (بدون باز کردن صفحه ویرایش) فیلدهایی مثل is_active رو تغییر بدی.

"""