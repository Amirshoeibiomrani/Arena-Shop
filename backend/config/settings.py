"""
تنظیمات اصلی پروژه فروشگاه آنلاین
Django + DRF + JWT + CORS
"""
from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

# ===========================================
# مسیرها
# ===========================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================================
# امنیت (از فایل .env خونده می‌شه)
# ===========================================
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# ===========================================
# اپلیکیشن‌ها
# ===========================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',

    "apps.accounts",
    "apps.dashboard",
    "apps.orders",
    "apps.products",
]


# DJANGO_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
# ]

# THIRD_PARTY_APPS = [
#     'rest_framework',
#     'rest_framework_simplejwt',
#     'rest_framework_simplejwt.token_blacklist',
#     'corsheaders',
#     'django_filters',
#     'drf_spectacular',
# ]

# LOCAL_APPS = [
#     'apps.accounts',
#     'apps.products',
#     'apps.orders',
#     'apps.dashboard',
# ]

# INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# ===========================================
# Middleware
# ===========================================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # باید قبل از CommonMiddleware باشه
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ===========================================
# دیتابیس - PostgreSQL
# ===========================================
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE'),
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

# ===========================================
# اعتبارسنجی رمز عبور
# ===========================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
]

# ===========================================
# مدل کاربر سفارشی (در گام بعدی می‌سازیم)
# ===========================================
AUTH_USER_MODEL = 'accounts.User'

# ===========================================
# زبان فارسی + تهران
# ===========================================
LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

# ===========================================
# فایل‌های استاتیک و مدیا
# ===========================================
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===========================================
# تنظیمات Django REST Framework
# ===========================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # DEFAULT_AUTHENTICATION_CLASSES: برای احراز هویت از JWT استفاده کن

    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        # DEFAULT_PERMISSION_CLASSES: کاربر لاگین نکرده فقط می‌تونه بخونه، نمی‌تونه تغییر بده

    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
    # PAGE_SIZE: 12: هر صفحه ۱۲ آیتم نشون بده

    'DEFAULT_FILTER_BACKENDS': (
        # DEFAULT_FILTER_BACKENDS: امکان فیلتر، جستجو و مرتب‌سازی

        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ===========================================
# تنظیمات JWT (Simple JWT)
# ===========================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),       # عمر توکن دسترسی
    # ACCESS_TOKEN_LIFETIME: 60 دقیقه: توکن کاربر هر یک ساعت یه بار باید رفرش بشه
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),          # عمر توکن رفرش
    # REFRESH_TOKEN_LIFETIME: 7 روز: توکن رفرش یه هفته اعتبار داره
    'ROTATE_REFRESH_TOKENS': True,                        # هر بار رفرش، توکن جدید بده
    # ROTATE_REFRESH_TOKENS: هر بار که رفرش زدیم، یه توکن جدید بساز (امن‌تره)
    'BLACKLIST_AFTER_ROTATION': True,
                                              # توکن قدیمی رو بلاک کن
                                            #   BLACKLIST_AFTER_ROTATION: توکن قدیمی رو بلاک کن که قابل استفاده مجدد نباشه
    'AUTH_HEADER_TYPES': ('Bearer',),                     # نوع هدر: Bearer <token>
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# ===========================================
# تنظیمات CORS (دسترسی فرانت Next.js)
# ===========================================
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())
CORS_ALLOW_CREDENTIALS = True

# ===========================================
# تنظیمات Swagger / OpenAPI
# ===========================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'Shop API',
    'DESCRIPTION': 'API فروشگاه آنلاین',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}