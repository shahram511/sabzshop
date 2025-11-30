from rest_framework import permissions

class IsAdminFromTehran(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser and request.user.city == 'تهران'


class IsBuyer(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return obj.buyer == request.user