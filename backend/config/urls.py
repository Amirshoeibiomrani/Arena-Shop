"""
URL های اصلی پروژه
ساختار: همه API ها زیر /api/v1/ قرار می‌گیرن (versioning استاندارد)
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# همه API ها زیر /api/v1/ قرار می‌گیرن
api_v1_patterns = [
    path('auth/', include('apps.accounts.urls')),
    # include('apps.accounts.urls')	به Django می‌گه: «برو URL های اپ accounts رو هم بخون»
    path('products/', include('apps.products.urls')),
    path('orders/', include('apps.orders.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
]
# api_v1_patterns	همه API ها زیر /api/v1/ گروه می‌شن (versioning)

urlpatterns = [
    # پنل ادمین
    path('admin/', admin.site.urls),

    # API ها
    path('api/v1/', include(api_v1_patterns)),

    # مستندات API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
# Spectacular...	Swagger و ReDoc برای مستندات تعاملی API


# سرو کردن فایل‌های مدیا در حالت توسعه
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # 	تو حالت Debug، عکس‌های آپلودی رو از طریق URL سرو می‌کنه


    # 📚 چرا /api/v1/؟
# وقتی بعداً API رو تغییر دادی، می‌تونی /api/v2/ بسازی و کاربران قدیمی همچنان از /api/v1/ استفاده کنن. این یه پرکتیس حرفه‌ایه.