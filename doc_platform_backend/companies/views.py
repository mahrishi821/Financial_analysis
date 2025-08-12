from rest_framework import viewsets
from .models import Company
from .serializers import CompanySerializer
from rest_framework.views import APIView
from common.jsonResponse.response import JSONResponseSender
from common.httpClient.httpClient import HttpClient

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().order_by('-created_at')
    serializer_class = CompanySerializer
