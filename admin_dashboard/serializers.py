from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from main.models import Student, Sponsor, StudentSponsor, INDIVIDUAL, LEGAL_ENTITY
from django.db.models import Sum


class SponsorSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    money_spent = serializers.SerializerMethodField()

    class Meta:
        model = Sponsor
        fields = [
            'id',
            'full_name',
            'phone_number',
            'total_sponsorship_amount',
            'money_spent',
            'created_at',
            'updated_at',
            'status',
            'company_name',
            'payment_type',
            'sponsor_type'
        ]


    def get_money_spent(self, obj):
        result = StudentSponsor.objects.filter(sponsor=obj).aggregate(total=Sum('allocated_money'))
        return result['total'] or 0


    def validate(self, attrs):
        instance = getattr(self, 'instance', None)  # when updating a sponsor, it attaches instance to it.
        company_name = attrs.get('company_name')
        sponsor_type = attrs.get('sponsor_type')

        if sponsor_type == LEGAL_ENTITY and not company_name:
            raise ValidationError(
                {
                    'success': False,
                    'message': 'Company name is required for legal entities.'
                }
            )

        if instance and instance.sponsor_type == LEGAL_ENTITY and sponsor_type == INDIVIDUAL:
            attrs['company_name'] = None  # Clear company name field when changing from legal entity to individual

        if sponsor_type == INDIVIDUAL and company_name:
            raise ValidationError(
                {
                    'success': False,
                    'message': 'Individuals should not have company name.'
                }
            )

        return attrs


class StudentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    covered_tuition_fee = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'full_name', 'phone_number', 'university', 'degree', 'tuition_fee', 'covered_tuition_fee', 'created_at', 'updated_at']

    def get_covered_tuition_fee(self, obj):
        result = StudentSponsor.objects.filter(student=obj).aggregate(total=Sum('allocated_money'))
        return result['total'] or 0


class StudentSponsorSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    sponsor = SponsorSerializer(read_only=True)
    sponsor_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = StudentSponsor
        fields = ['id', 'sponsor', 'sponsor_id', 'allocated_money']


    def validate(self, attrs):
        sponsor_id = attrs.get('sponsor_id')

        if sponsor_id:
            if not Sponsor.objects.filter(id=sponsor_id).exists():
                raise ValidationError(
                    {
                        'success': False,
                        'message': 'There is no sponsor found with this id.'
                    }
                )

        return attrs

