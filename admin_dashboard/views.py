from django.db.models import Q, Sum
from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from shared.custom_pagination import CustomPagination
from .serializers import SponsorSerializer, StudentSerializer, StudentSponsorSerializer
from shared.permissions import IsStaffUser
from main.models import Sponsor, Student, StudentSponsor
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from datetime import datetime
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from rest_framework.exceptions import ValidationError


# Sponsor

@extend_schema(
        request=SponsorSerializer,
        tags=["sponsors"],
        description="""
        Lists all sponsors with optional search and filtering.
        """,
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                description="Search sponsors by full name."
            ),
            OpenApiParameter(
                name='status',
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter sponsors by status (e.g., 'new', 'in_progress', 'verified', 'cancelled')."
            ),
            OpenApiParameter(
                name='amount',
                type=int,
                location=OpenApiParameter.QUERY,
                description="Filter sponsors by sponsorship amount greater than or equal to this value."
            ),
            OpenApiParameter(
                name='start_date',
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter sponsors created after this date. Input pattern (format: DD-MM-YYYY)"
            ),
            OpenApiParameter(
                name='end_date',
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter sponsors created before this date (format: DD-MM-YYYY)"
            )
        ]
    )
class SponsorListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsStaffUser]
    serializer_class = SponsorSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        # Searching
        search = self.request.query_params.get('search', '')
        # Filtering
        application_status = self.request.query_params.get('status', None)
        total_sponsorship_amount = self.request.query_params.get('amount', None)  # This searches for what is greater than the amount
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        filters = Q()

        filters &= Q(full_name__icontains=search)

        if application_status:
            if application_status not in ['new', 'in_progress', 'verified', 'cancelled']:
                raise ValidationError({'status': 'Invalid status.'})
            filters &= Q(status__iexact=application_status)

        if total_sponsorship_amount:
            try:
                total_sponsorship_amount = int(total_sponsorship_amount)
                filters &= Q(total_sponsorship_amount__gte=total_sponsorship_amount)
            except ValueError:
                raise ValidationError({'amount': 'Amount must be a valid integer.'})

        if start_date:
            try:
                parsed_date = datetime.strptime(start_date, '%d-%m-%Y').date()
                filters &= Q(created_at__date__gte=parsed_date)
            except ValueError:
                raise ValidationError({'start_date': "Invalid date format"})

        if end_date:
            try:
                parsed_date = datetime.strptime(end_date, '%d-%m-%Y').date()
                filters &= Q(created_at__date__lte=parsed_date)
            except ValueError as e:
                raise ValidationError({'end_date': "Invalid date format"})

        sponsors = Sponsor.objects.filter(filters)
        return sponsors

@extend_schema(
    request=SponsorSerializer,
    tags=['sponsors'],
    description="""
    Retrieve, update, delete sponsor data.
    Update sponsor data using one's id.
            Choice fields when updating sponsor data:
            Sponsor types -> individual, legal_entity  # Jismoniy shaxs, Yuridik shaxs
            Payment methods -> cash, debit_card, bank_transfer  # Naqt, karta, bank orqali
            Sponsor application status -> new, in_progress, verified, cancelled  # Yangi, Jarayonda, Tasdiqlandi, Rad etildi
    """
)
class SponsorDetailUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsStaffUser]
    serializer_class = SponsorSerializer
    queryset = Sponsor.objects.all()
    lookup_field = 'id'


# Student

@extend_schema(
        request=StudentSerializer,
        tags=['students'],
        description="""
        Create new student.
            Choice fields needed when creating new student:
            Student degrees -> bachelor, master  # Bakalavr, Magistr
        """,
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                description="Search students by full name."
            ),
            OpenApiParameter(
                name='degree',
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter students by degree. ('bachelor', 'master')"
            ),
            OpenApiParameter(
                name='university',
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter students by university."
            )
        ]
    )
class StudentListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsStaffUser]
    serializer_class = StudentSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        # Searching
        search = self.request.query_params.get('search', '')
        # Filtering
        degree = self.request.query_params.get('degree', None)
        university = self.request.query_params.get('university', None)

        filters = Q()

        filters &= Q(full_name__icontains=search)

        if degree:
            if degree not in ['bachelor', 'master']:
                raise ValidationError({'degree': 'Invalid degree. Degree must be one of them ("bachelor", "master")'})
            filters &= Q(degree__iexact=degree)

        if university:
            filters &= Q(university__iexact=university)

        students = Student.objects.filter(filters)
        return students


@extend_schema(
        request=StudentSerializer,
        tags=['students'],
        description="""
        Retrieve, Update, Delete student.
        Update student data with id.
            Choice fields needed when updating the student data:
            Student degrees -> bachelor, master  # Bakalavr, Magistr
        """
    )
class StudentDetailUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsStaffUser]
    serializer_class = StudentSerializer
    queryset = Student.objects.all()
    lookup_field = 'id'


# StudentSponsor


@extend_schema(
        request=StudentSponsorSerializer,
        tags=['student sponsors']
    )
class StudentSponsorListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsStaffUser]
    serializer_class = StudentSponsorSerializer


    @staticmethod
    def get_student(student_id):
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            raise Http404('Student with this id does not exist.')
        return student

    def get_queryset(self):
        student_id = self.kwargs.get('student_id')
        student=self.get_student(student_id)

        return StudentSponsor.objects.filter(student=student)

    def perform_create(self, serializer):
        student_id = self.kwargs.get('student_id')
        student = self.get_student(student_id)

        serializer.save(student=student)


@extend_schema(
    request=StudentSponsorSerializer,
    tags=['student sponsors']
)
class StudentSponsorDetailUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsStaffUser]
    serializer_class = StudentSponsorSerializer

    def get_object(self):
        student_id = self.kwargs.get('student_id')
        sponsor_id = self.kwargs.get('sponsor_id')
        obj = StudentSponsor.objects.filter(student_id=student_id, sponsor_id=sponsor_id).first()
        if not obj:
            raise Http404("StudentSponsor record not found.")
        return obj


class StudentSponsorSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]

    @extend_schema(
        tags=['student sponsors']
    )
    def get(self, request):
        student_count = Student.objects.count()
        sponsor_count = Sponsor.objects.count()
        total_paid_tuition_fee = StudentSponsor.objects.all().aggregate(total=Sum('allocated_money'))['total'] or 0
        total_asked_amount = Student.objects.all().aggregate(total=Sum('tuition_fee'))['total'] or 0
        remaining_unpaid_amount = total_asked_amount - total_paid_tuition_fee

        return Response(
            {
                'student_count': student_count,
                'sponsor_count': sponsor_count,
                'total_paid_amount': total_paid_tuition_fee,
                'total_asked_amount': total_asked_amount,
                'remaining_unpaid_amount': remaining_unpaid_amount
            }
        )

