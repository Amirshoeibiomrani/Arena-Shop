"""
Permission های مخصوص داشبورد
"""
from rest_framework import permissions


class IsStaffUser(permissions.BasePermission):
    """فقط کاربران staff (ادمین) دسترسی دارن"""
    message = 'شما به این بخش دسترسی ندارید.'

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )