"""
ثبت مدل‌های accounts در پنل ادمین
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """پنل ادمین سفارشی برای کاربران"""

    list_display = ('email', 'username', 'phone', 'is_verified', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_verified', 'is_active', 'date_joined')
    search_fields = ('email', 'username', 'phone', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    # تنظیم فیلدهایی که در صفحه ویرایش نشون داده می‌شن
    fieldsets = BaseUserAdmin.fieldsets + (
        ('اطلاعات تکمیلی', {
            'fields': ('phone', 'avatar', 'address', 'is_verified'),
        }),
    )

    # فیلدهای صفحه ساخت کاربر جدید
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('اطلاعات تکمیلی', {
            'fields': ('email', 'phone'),
        }),
    )


    """📚 چی شد؟

@admin.register(User) → User رو تو ادمین ثبت کن
list_display → ستون‌هایی که تو لیست کاربران نشون داده می‌شن
list_filter → فیلترهای کنار صفحه
search_fields → فیلدهای قابل جستجو
fieldsets → فیلدهای داخل صفحه ویرایش
"""