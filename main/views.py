from rest_framework.permissions import AllowAny
from rest_framework import generics
from .serializers import SponsorApplicationSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema(
    request=SponsorApplicationSerializer,
    tags=['sponsors'],
    description="""
        Apply for becoming sponsor.
        Choice fields needed for application:
        Sponsor types -> individual, legal_entity  # Jismoniy shaxs, Yuridik shaxs
        Payment methods -> cash, debit_card, bank_transfer  # Naqt, karta, bank orqali
        """
)
class SponsorApplicationAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = SponsorApplicationSerializer

