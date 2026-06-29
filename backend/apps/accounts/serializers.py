"""
Serializer های اپ accounts
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


# ============================================
# 1. Serializer ثبت‌نام (Register)
# ============================================
class RegisterSerializer(serializers.ModelSerializer):
    """ثبت‌نام کاربر جدید با تایید رمز عبور"""

# از ModelSerializer ارث می‌بره (یعنی خودکار از روی مدل User می‌خونه)

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='تکرار رمز عبور',
    )
# password و password2 فقط write only هستن (یعنی موقع خوندن برنمی‌گردن - امنیت)


    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password', 'password2')
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
        }

    def validate(self, attrs):
        """چک می‌کنه دو رمز عبور یکی باشن"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "رمز عبور و تکرار آن یکسان نیستند."}
            )
        return attrs

    def create(self, validated_data):
        """کاربر جدید رو می‌سازه (رمز عبور هش می‌شه)"""
        validated_data.pop('password2')  # password2 رو از دیتا حذف کن
        user = User.objects.create_user(**validated_data)
        return user


# ============================================
# 2. Serializer JWT سفارشی (Login)
# ============================================
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer لاگین.
    علاوه بر توکن، اطلاعات کاربر رو هم برمی‌گردونه.

     CustomTokenObtainPairSerializer
ما توکن JWT پیش‌فرض رو سفارشی کردیم
علاوه بر access و refresh توکن، اطلاعات کاربر هم برمی‌گرده
این یعنی فرانت بعد از لاگین، نیازی نیست یه درخواست جدا برای گرفتن اطلاعات کاربر بزنه

    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # اطلاعات اضافه که داخل توکن قرار می‌گیره
        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # اطلاعات کاربر رو همراه توکن برگردون
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'full_name': self.user.full_name,
            'is_staff': self.user.is_staff,
        }
        return data


# ============================================
# 3. Serializer پروفایل کاربر
# ============================================
class UserProfileSerializer(serializers.ModelSerializer):
    """نمایش و ویرایش پروفایل کاربر"""


# UserProfileSerializer
# نمایش و ویرایش پروفایل
# بعضی فیلدها read_only هستن (مثل ایمیل که نمی‌شه تغییر داد)


    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'phone', 'avatar', 'address',
            'is_verified', 'date_joined',
        )
        read_only_fields = ('id', 'username', 'email', 'is_verified', 'date_joined')


# ============================================
# 4. Serializer تغییر رمز عبور
# ============================================
class ChangePasswordSerializer(serializers.Serializer):
    """تغییر رمز عبور با تایید رمز قبلی"""

#  ChangePasswordSerializer
# نه از ModelSerializer بلکه از Serializer ساده ارث می‌بره (چون با مدل کار نمی‌کنه)
# اول چک می‌کنه رمز قبلی درسته
# بعد رمز جدید رو با اعتبارسنجی Django چک می‌کنه


    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
    )
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError(
                {"new_password": "رمز جدید و تکرار آن یکسان نیستند."}
            )
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("رمز عبور فعلی نادرست است.")
        return value



    """
    Serializer چیه؟ 🤔

Serializer یعنی «تبدیل‌کننده». کارش اینه که:

داده‌های Python (مدل‌های Django) رو به JSON تبدیل کنه (برای ارسال به فرانت)
داده‌های JSON ورودی رو به Python تبدیل و اعتبارسنجی کنه
می‌تونی فکر کنی Serializer مثل فرم Django ولی برای API.
    """

# ============================================
# 5. Serializer لیست کاربران (برای ادمین)
# ============================================
class UserAdminListSerializer(serializers.ModelSerializer):
    """نمایش کاربر برای پنل ادمین"""
    full_name = serializers.CharField(read_only=True)
    orders_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'phone', 'avatar', 'is_active', 'is_staff',
            'is_verified', 'orders_count', 'date_joined',
        )


# ============================================
# 6. Serializer ساخت/ویرایش کاربر (برای ادمین)
# ============================================
class UserAdminCreateUpdateSerializer(serializers.ModelSerializer):
    """ساخت و ویرایش کاربر توسط ادمین"""
    password = serializers.CharField(
        write_only=True, required=False, allow_blank=True, min_length=6
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'phone', 'password', 'is_active', 'is_staff', 'is_verified',
        )
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({"password": "رمز عبور الزامی است."})
        user = User.objects.create_user(password=password, **validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance