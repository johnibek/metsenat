from django.db.models import Q, Sum
from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from shared.custom_pagination import CustomPagination
from .serializers import SponsorSerializer, StudentSerializer, StudentSponsorSerializer
from .permissions import IsStaffUser
from main.models import Sponsor, Student, StudentSponsor
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime
from drf_spectacular.utils import extend_schema

# Sponsor

class SponsorListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]

    @extend_schema(
        request=SponsorSerializer,
        tags=["sponsors"]
    )
    def get(self, request):
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
            filters &= Q(status__iexact=application_status)

        if total_sponsorship_amount:
            try:
                total_sponsorship_amount = int(total_sponsorship_amount)
                filters &= Q(total_sponsorship_amount__gte=total_sponsorship_amount)
            except ValueError:
                pass

        if start_date:
            try:
                parsed_date = datetime.strptime(start_date, '%d-%m-%Y').date()
                filters &= Q(created_at__date__gte=parsed_date)
            except ValueError:
                pass

        if end_date:
            try:
                parsed_date = datetime.strptime(end_date, '%d-%m-%Y').date()
                filters &= Q(created_at__date__lte=parsed_date)
            except ValueError:
                pass

        sponsors = Sponsor.objects.filter(filters)

        paginator = CustomPagination()
        page_obj = paginator.paginate_queryset(sponsors, request)
        serializer = SponsorSerializer(page_obj, many=True)

        return paginator.get_paginated_response(serializer.data)


class SponsorDetailUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]

    @staticmethod
    def get_sponsor(id):
        try:
            sponsor = Sponsor.objects.get(id=id)
        except Sponsor.DoesNotExist:
            raise Http404("Sponsor with this id does not exist.")
        return sponsor

    @extend_schema(
        request=SponsorSerializer,
        tags=['sponsors']
    )
    def get(self, request, id):
        sponsor = self.get_sponsor(id)

        serializer = SponsorSerializer(sponsor, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=SponsorSerializer,
        description="""
            Update sponsor data using one's id.
            Choice fields when updating sponsor data:
            Sponsor types -> individual, legal_entity  # Jismoniy shaxs, Yuridik shaxs
            Payment methods -> cash, debit_card, bank_transfer  # Naqt, karta, bank orqali
            Sponsor application status -> new, in_progress, verified, cancelled  # Yangi, Jarayonda, Tasdiqlandi, Rad etildi
        """,
        tags=['sponsors']
    )
    def put(self, request, id):
        sponsor = self.get_sponsor(id)
        serializer = SponsorSerializer(instance=sponsor, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=SponsorSerializer,
        tags=['sponsors'],
        description="""
                Update sponsor data using one's id.
                Choice fields when updating sponsor data:
                Sponsor types -> individual, legal_entity  # Jismoniy shaxs, Yuridik shaxs
                Payment methods -> cash, debit_card, bank_transfer  # Naqt, karta, bank orqali
                Sponsor application status -> new, in_progress, verified, cancelled  # Yangi, Jarayonda, Tasdiqlandi, Rad etildi
            """
    )
    def patch(self, request, id):
        sponsor = self.get_sponsor(id)
        serializer = SponsorSerializer(instance=sponsor, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=SponsorSerializer,
        tags=['sponsors']
    )
    def delete(self, request, id):
        sponsor = self.get_sponsor(id)
        sponsor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Student

class StudentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]

    @extend_schema(
        request=StudentSerializer,
        tags=['students']
    )
    def get(self, request):
        # Searching
        search = self.request.query_params.get('search', '')
        # Filtering
        degree = self.request.query_params.get('degree', None)
        university = self.request.query_params.get('university', None)

        filters = Q()

        filters &= Q(full_name__icontains=search)

        if degree:
            filters &= Q(degree__iexact=degree)

        if university:
            filters &= Q(university__iexact=university)

        students = Student.objects.filter(filters)

        paginator = CustomPagination()
        page_obj = paginator.paginate_queryset(students, request)

        serializer = StudentSerializer(page_obj, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        request=StudentSerializer,
        tags=['students'],
        description="""
            Create new student.
            Choice fields needed when creating new student:
            Student degrees -> bachelor, master  # Bakalavr, Magistr
        """
    )
    def post(self, request):
        serializer = StudentSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StudentDetailUpdateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]

    @staticmethod
    def get_student(id):
        try:
            student = Student.objects.get(id=id)
        except Student.DoesNotExist:
            raise Http404("Student with this id does not exist.")
        return student

    @extend_schema(
        request=StudentSerializer,
        tags=['students']
    )
    def get(self, request, id):
        student = self.get_student(id)
        serializer = StudentSerializer(instance=student, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=StudentSerializer,
        tags=['students'],
        description="""
                Update student data using one's id.
                Choice fields needed when updating the student data:
                Student degrees -> bachelor, master  # Bakalavr, Magistr
            """
    )
    def put(self, request, id):
        student = self.get_student(id)
        serializer = StudentSerializer(instance=student, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=StudentSerializer,
        tags=['students'],
        description="""
                    Update student data using one's id.
                    Choice fields needed when updating the student data:
                    Student degrees -> bachelor, master  # Bakalavr, Magistr
                """
    )
    def patch(self, request, id):
        student = self.get_student(id)
        serializer = StudentSerializer(instance=student, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=StudentSerializer,
        tags=['students']
    )
    def delete(self, request, id):
        student = self.get_student(id)
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# StudentSponsor

class StudentSponsorListCreate(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]

    @staticmethod
    def get_student(student_id):
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            raise Http404('Student with this id does not exist.')
        return student

    @extend_schema(
        request=StudentSponsorSerializer,
        tags=['student sponsors']
    )
    def get(self, request, student_id):
        student = self.get_student(student_id)

        student_sponsors = StudentSponsor.objects.filter(student=student)
        serializer = StudentSponsorSerializer(student_sponsors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=StudentSponsorSerializer,
        tags=['student sponsors']
    )
    def post(self, request, student_id):
        student = self.get_student(student_id)
        serializer = StudentSponsorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(student=student)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StudentSponsorDetailUpdateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]

    @staticmethod
    def get_student_sponsor(student_id, sponsor_id):
        try:
            student_sponsor = StudentSponsor.objects.get(student_id=student_id, sponsor_id=sponsor_id)
        except StudentSponsor.DoesNotExist:
            raise Http404("Student Sponsor with this id does not exist.")
        return student_sponsor

    @extend_schema(
        request=StudentSponsorSerializer,
        tags=['student sponsors']
    )
    def get(self, request, student_id, sponsor_id):
        student_sponsor = self.get_student_sponsor(student_id, sponsor_id)
        serializer = StudentSponsorSerializer(instance=student_sponsor)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=StudentSponsorSerializer,
        tags=['student sponsors']
    )
    def put(self, request, student_id, sponsor_id):
        student_sponsor = self.get_student_sponsor(student_id, sponsor_id)
        serializer = StudentSponsorSerializer(instance=student_sponsor, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=StudentSponsorSerializer,
        tags=['student sponsors']
    )
    def patch(self, request, student_id, sponsor_id):
        student_sponsor = self.get_student_sponsor(student_id, sponsor_id)
        serializer = StudentSponsorSerializer(instance=student_sponsor, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=StudentSponsorSerializer,
        tags=['student sponsors']
    )
    def delete(self, request, student_id, sponsor_id):
        student_sponsor = self.get_student_sponsor(student_id, sponsor_id)
        student_sponsor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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

