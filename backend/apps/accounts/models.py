from django.db import models

# Create your models here.
"""
مدل کاربر سفارشی
از AbstractUser ارث‌بری می‌کنیم تا بتونیم فیلدهای دلخواه (مثل موبایل و آواتار) اضافه کنیم.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    """کاربر سفارشی - ایمیل به جای username برای ورود استفاده می‌شه"""

    email = models.EmailField('ایمیل', unique=True)

    phone_regex = RegexValidator(
        regex=r'^09\d{9}$',
        message="شماره موبایل باید با 09 شروع بشه و 11 رقم باشه"
    )
    # این یعنی شماره موبایل باید با 09 شروع بشه و دقیقاً ۱۱ رقم باشه. مثلاً 09123456789.
# blank=True, null=True یعنی شماره موبایل اختیاریه.



    phone = models.CharField(
        'شماره موبایل',
        validators=[phone_regex],
        max_length=11,
        blank=True,
        null=True,
    )

    avatar = models.ImageField(
        'تصویر پروفایل',
        upload_to='avatars/',
        blank=True,
        null=True,
    )
# 🖼️ avatar = models.ImageField(...)
# تصویر پروفایل که داخل media/avatars/ ذخیره می‌شه.


    address = models.TextField('آدرس', blank=True, null=True)

    is_verified = models.BooleanField('تایید شده', default=False)
    created_at = models.DateTimeField('تاریخ ثبت‌نام', auto_now_add=True)
    updated_at = models.DateTimeField('تاریخ بروزرسانی', auto_now=True)

    # ایمیل به عنوان فیلد اصلی ورود
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # برای دستور createsuperuser
# 🔐 USERNAME_FIELD = 'email'
# این مهم‌ترین خط مدله! به Django می‌گه: "کاربر با ایمیل لاگین می‌کنه، نه username." این روش استاندارد امروزه.

# 🎁 @property full_name
# یه property محاسباتی. هر جا بنویسی user.full_name، اسم کاملش رو می‌ده. اگه اسم و فامیلی نداشت، username رو برمی‌گردونه.


    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ['-created_at']

    def __str__(self):
        return self.email or self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username



    # از کلاس AbstractUser ارث‌بری می‌کنیم. یعنی همه فیلدهای پیش‌فرض Django (username, password, first_name, last_name, ...) رو رایگان داریم و فقط فیلدهای جدید اضافه می‌کنیم.

# 💡 چرا AbstractUser و نه AbstractBaseUser؟
# AbstractUser ساده‌تره و فیلدهای آماده داره. AbstractBaseUser کاملاً خام هست و باید همه چی رو خودت بسازی. برای ۹۰٪ پروژه‌ها AbstractUser کافیه.



# 📧 email = models.EmailField('ایمیل', unique=True)
# 'ایمیل' → اسم فارسی که تو پنل ادمین نشون داده می‌شه
# unique=True → دو کاربر نمی‌تونن ایمیل یکسان داشته باشن