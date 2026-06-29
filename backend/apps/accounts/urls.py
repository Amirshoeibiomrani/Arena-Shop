"""
URL های اپ accounts
همه این URL ها زیر /api/v1/auth/ قرار می‌گیرن
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    ChangePasswordView,
)

urlpatterns = [
    # ثبت‌نام و ورود
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # مدیریت توکن
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # پروفایل و رمز عبور
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]


"""📚 لیست نهایی API ها:
متد	آدرس	کاربرد
POST	/api/v1/auth/register/	ثبت‌نام
POST	/api/v1/auth/login/	ورود
POST	/api/v1/auth/logout/	خروج
POST	/api/v1/auth/token/refresh/	تازه کردن توکن
POST	/api/v1/auth/token/verify/	اعتبارسنجی توکن
GET/PUT/PATCH	/api/v1/auth/profile/	پروفایل
POST	/api/v1/auth/change-password/	تغییر رمز
"""