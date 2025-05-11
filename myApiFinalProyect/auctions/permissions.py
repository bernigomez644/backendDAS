from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsRatingOwnerOrAdmin(BasePermission):
    """
    Permite acceso si el usuario es el creador de la valoración (user) o es administrador.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """
    Permite editar/eliminar una subasta solo si el usuario es el propietario
    o es administrador. Cualquiera puede consultar (GET).
    """

    def has_object_permission(self, request, view, obj):
        # Permitir acceso de lectura a cualquier usuario (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True

        # Permitir si el usuario es el creador o es administrador
        return obj.auctioneer == request.user or request.user.is_staff


class IsBidOwnerOrAdmin(BasePermission):
    """
    Solo el propietario de la puja o un administrador puede editarla o eliminarla.
    Todos pueden leer.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True  # Ver está permitido
        return obj.bidder == request.user or request.user.is_staff


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True  # GET, HEAD, OPTIONS permitidos a todos
        return request.user and request.user.is_staff
