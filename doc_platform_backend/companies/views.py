from urllib import request

from rest_framework import viewsets
from common.models import Company
from common.serializers import UserSignupSerializer, UserLoginSerializer,CompanySerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from common.jsonResponse.response import JSONResponseSender



class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().order_by('-created_at')
    serializer_class = CompanySerializer

    @action(detail=False, methods=['get'])
    def company_count(self,request):
        try:
            user=request.user
            company_count = Company.objects.all().filter(created_by=user).count()
            return JSONResponseSender.send_success( {"company_count":company_count})
        except Exception as e:
            return JSONResponseSender.send_error("500", str(e),str(e))

    # / api / companies / company_count /
class SignupView(APIView):
    serializer_class = UserSignupSerializer
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return JSONResponseSender.send_success("User created successfully")
        except Exception as e:
            return JSONResponseSender.send_error("500","Error creating user", str(e))

class LoginView(APIView):
    serializer_class = UserLoginSerializer

    permission_classes = [AllowAny]
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.create_tokens(serializer.validated_data['user'])
        return JSONResponseSender.send_success(tokens)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return JSONResponseSender.send_error("Refresh token required")

            token = RefreshToken(refresh_token)
            token.blacklist()

            return JSONResponseSender.send_success("Logged out successfully")
        except Exception as e:
            return JSONResponseSender.send_error(500, str(e), str(e))

