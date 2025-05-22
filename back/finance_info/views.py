from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import FinanceInfo
from .serializers import FinanceInfoSerializer

class FinanceInfoViewSet(viewsets.ModelViewSet):
    queryset = FinanceInfo.objects.all()
    serializer_class = FinanceInfoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]