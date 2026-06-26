from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import LogmanUser
from accounts.permissions import IsSuperAdminOrReadOnly
from accounts.serializers import (
    UserSerializer,
    ProfileSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class UserViewSet(viewsets.ModelViewSet):
    """User management. Listing/creating/editing/deleting users is restricted to
    super admins; every authenticated user can read and edit their own profile
    and change their password via the `me` / `change-password` actions."""
    queryset = LogmanUser.objects.all().order_by('-is_active', 'email')
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ('me', 'change_password'):
            return [IsAuthenticated()]
        # Everyone authenticated may view users; only super admins may manage them.
        return [IsSuperAdminOrReadOnly()]

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        if request.method.lower() == 'patch':
            serializer = ProfileSerializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response(ProfileSerializer(request.user).data)

    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password updated successfully.'}, status=status.HTTP_200_OK)


class CustomTokenObtainpairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
