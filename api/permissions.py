from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    소유자만 수정 가능, 나머지는 읽기만 가능
    """
    def has_object_permission(self, request, view, obj):
        # 읽기 권한은 모든 사용자에게 허용
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 쓰기 권한은 소유자에게만 허용
        return obj.owner == request.user

class IsOwner(permissions.BasePermission):
    """
    소유자만 접근 가능
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user