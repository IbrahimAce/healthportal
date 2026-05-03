"""
API URL routes for accounts.
SimpleJWT provides login (/token/) and refresh (/token/refresh/) out of the box.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterAPIView, MeAPIView

urlpatterns = [
    path("auth/register/", RegisterAPIView.as_view(), name="api-register"),
    path("auth/login/",    TokenObtainPairView.as_view(), name="api-login"),
    path("auth/refresh/",  TokenRefreshView.as_view(), name="api-token-refresh"),
    path("auth/me/",       MeAPIView.as_view(), name="api-me"),
]
