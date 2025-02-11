from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import SponsorApplicationSerializer
from drf_spectacular.utils import extend_schema


class SponsorApplicationAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=SponsorApplicationSerializer,
        tags=["sponsors"],
        description="""
        Apply for becoming sponsor.
        Choice fields needed for application:
        Sponsor types -> individual, legal_entity  # Jismoniy shaxs, Yuridik shaxs
        Payment methods -> cash, debit_card, bank_transfer  # Naqt, karta, bank orqali
        """
    )
    def post(self, request):
        serializer = SponsorApplicationSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = serializer.data
        response.update(
            {
                'success': True,
                'message': 'Application Successful.'
            }
        )

        return Response(response, status=status.HTTP_201_CREATED)

