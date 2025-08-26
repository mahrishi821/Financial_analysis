from rest_framework import viewsets
from common.models import Company
from common.serializers import UserSignupSerializer, UserLoginSerializer,CompanySerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from common.jsonResponse.response import JSONResponseSender
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().order_by('-created_at')
    serializer_class = CompanySerializer

class SignupView(APIView):
    serializer_class = UserSignupSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return JSONResponseSender.send_success("User created successfully")

class LoginView(APIView):
    serializer_class = UserLoginSerializer

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
                token.blacklist()  # This makes the refresh token unusable

                return JSONResponseSender.send_success("Logged out successfully")
            except Exception as e:
                return JSONResponseSender.send_error(500,str(e),str(e))