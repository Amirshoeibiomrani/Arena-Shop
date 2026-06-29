"""
View های اپ accounts
"""
from django.contrib.auth import get_user_model
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()

# کلاس‌های Generic
# Django REST Framework یه عالمه کلاس آماده داره که کارمون رو خیلی راحت می‌کنه:

"""کلاس	کاربرد
CreateAPIView	فقط ساخت (POST)
RetrieveUpdateAPIView	دیدن و ویرایش (GET, PUT, PATCH)
APIView	ساده‌ترین کلاس، خودت همه چی رو بنویسی
"""
# ============================================
# 1. ثبت‌نام
# ============================================
class RegisterView(generics.CreateAPIView):
    """
    ثبت‌نام کاربر جدید
    POST /api/v1/auth/register/
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
# permission_classes
# AllowAny → همه می‌تونن دسترسی داشته باشن (ثبت‌نام، ورود)
# IsAuthenticated → فقط کاربران لاگین‌کرده (پروفایل، خروج)


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # ساخت توکن برای کاربر تازه ثبت‌نام شده
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'ثبت‌نام با موفقیت انجام شد',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)


# ============================================
# 2. ورود (Login)
# ============================================
class LoginView(TokenObtainPairView):
    """
    ورود با ایمیل و رمز عبور
    POST /api/v1/auth/login/
    """
    serializer_class = CustomTokenObtainPairSerializer


# ============================================
# 3. خروج (Logout)
# ============================================
class LogoutView(APIView):
    """
    خروج کاربر - توکن refresh رو بلاک می‌کنه
    POST /api/v1/auth/logout/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'توکن refresh الزامی است'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            # چرا blacklist()؟
            # وقتی کاربر logout می‌کنه، فقط حذف توکن از فرانت کافی نیست - چون کسی که توکن رو دزدیده می‌تونه باهاش وارد بشه. پس توکن رو بلاک می‌کنیم تا دیگه قابل استفاده نباشه.

            return Response(
                {'message': 'با موفقیت خارج شدید'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': 'توکن نامعتبر است'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================
# 4. پروفایل کاربر (مشاهده و ویرایش)
# ============================================
class ProfileView(generics.RetrieveUpdateAPIView):
    """
    مشاهده و ویرایش پروفایل
    GET  /api/v1/auth/profile/   → دیدن پروفایل
    PUT  /api/v1/auth/profile/   → ویرایش کامل
    PATCH /api/v1/auth/profile/  → ویرایش بخشی
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # همیشه پروفایل کاربر لاگین کرده رو برگردون
        return self.request.user


# ============================================
# 5. تغییر رمز عبور
# ============================================
class ChangePasswordView(APIView):
    """
    تغییر رمز عبور
    POST /api/v1/auth/change-password/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response(
            {'message': 'رمز عبور با موفقیت تغییر کرد'},
            status=status.HTTP_200_OK
        )