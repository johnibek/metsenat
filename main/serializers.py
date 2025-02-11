from rest_framework.exceptions import ValidationError

from .models import StudentSponsor, Student, Sponsor
from rest_framework import serializers
from .models import LEGAL_ENTITY, INDIVIDUAL


class SponsorApplicationSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Sponsor
        fields = ['id', 'sponsor_type', 'full_name', 'phone_number', 'payment_type', 'total_sponsorship_amount', 'company_name', 'description']

    def validate(self, attrs):
        sponsor_type = attrs.get('sponsor_type')
        company_name = attrs.get('company_name')

        if sponsor_type == LEGAL_ENTITY and not company_name:
            raise ValidationError(
                {
                    'success': False,
                    'message': 'Company name is required for legal entities.'
                }
            )

        if sponsor_type == INDIVIDUAL and company_name:
            raise ValidationError(
                {
                    'success': False,
                    'message': 'Individuals should not have company name.'
                }
            )

        return attrs
