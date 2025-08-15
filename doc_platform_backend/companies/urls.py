from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import CompanyViewSet, SignupView, LoginView
from rest_framework_simplejwt.views import  TokenRefreshView


router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')

urlpatterns = [
    path('signup/', SignupVigiew.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
urlpatterns += router.urls
