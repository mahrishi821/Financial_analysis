from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import CompanyViewSet, SignupView, LoginView, LogoutView,UserInfoView
from rest_framework_simplejwt.views import  TokenRefreshView


router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('userinfo/',UserInfoView.as_view(),name="userinfo"),
]
urlpatterns += router.urls
