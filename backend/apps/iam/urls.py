from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserIAMViewSet, IAMRuleViewSet, UserPermissionsViewSet, validate_token

router = DefaultRouter()
router.register(r'users', UserIAMViewSet, basename='iam-users')
router.register(r'rules', IAMRuleViewSet, basename='iam-rules')
router.register(r'permissions', UserPermissionsViewSet, basename='iam-permissions')

urlpatterns = [
    path('', include(router.urls)),
    path('validate-token/', validate_token, name='validate-token'),
]
