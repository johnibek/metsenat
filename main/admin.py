from django.contrib import admin
from .models import Student, Sponsor, StudentSponsor


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone_number', 'university', 'degree', 'tuition_fee', 'created_at', 'updated_at']
    search_fields = ['full_name']


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ['id', 'sponsor_type', 'full_name', 'phone_number', 'payment_type', 'total_sponsorship_amount', 'status']
    search_fields = ['full_name']


@admin.register(StudentSponsor)
class StudentSponsorAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'sponsor', 'allocated_money']
    search_fields = ['student__full_name', 'sponsor__full_name']
