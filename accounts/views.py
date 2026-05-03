"""
Auth API views — registration and current user profile.
JWT login/refresh/logout are handled by SimpleJWT endpoints (see api_urls.py).
"""

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, UserProfileSerializer


class RegisterAPIView(generics.CreateAPIView):
    """
    POST /api/v1/auth/register/
    Open endpoint — no authentication required.
    Creates a patient account and returns the user profile.
    """
    serializer_class   = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserProfileSerializer(user).data, status=201)


class MeAPIView(APIView):
    """
    GET /api/v1/auth/me/
    Returns the currently authenticated user's profile.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)
