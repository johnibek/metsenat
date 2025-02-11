from django.db import models
from django.db.models import Sum
from rest_framework.exceptions import ValidationError

from shared.models import BaseModel
from django.utils.translation import gettext as _
from django.core.validators import MinValueValidator


BACHELOR, MASTER = 'bachelor', 'master'
class Student(BaseModel):
    DEGREES = (
        (BACHELOR, _("Bachelor's degree")),
        (MASTER, _("Master's degree"))
    )

    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=13)
    university = models.CharField(max_length=100)
    degree = models.CharField(max_length=10, choices=DEGREES)
    tuition_fee = models.FloatField()

    class Meta:
        db_table = 'students'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'


    def __str__(self):
        return self.full_name


INDIVIDUAL, LEGAL_ENTITY = 'individual', 'legal_entity'
CASH, DEBIT_CARD, BANK_TRANSFER = 'cash', 'debit_card', 'bank_transfer'
NEW, IN_PROGRESS, VERIFIED, CANCELLED = 'new', 'in_progress', 'verified', 'cancelled'
class Sponsor(BaseModel):
    SPONSOR_TYPES = (
        (INDIVIDUAL, _("Individual")),  # Jismoniy shaxs
        (LEGAL_ENTITY, _("Legal Entity"))  # Yuridik shaxs
    )
    PAYMENT_TYPES = (
        (CASH, _("Cash")),
        (DEBIT_CARD, _("Debit Card")),
        (BANK_TRANSFER, _("Bank Transfer"))
    )
    STATUS_TYPES = (
        (NEW, _('New')),
        (IN_PROGRESS, _("In Progress")),
        (VERIFIED, _('Verified')),
        (CANCELLED, _('Cancelled'))
    )

    sponsor_type = models.CharField(max_length=50, choices=SPONSOR_TYPES)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=13)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    total_sponsorship_amount = models.FloatField(validators=[MinValueValidator(500000)])
    status = models.CharField(max_length=50, choices=STATUS_TYPES, default=NEW)
    company_name = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'sponsors'
        verbose_name = "Sponsor"
        verbose_name_plural = 'Sponsors'

    def clean(self):
        if self.sponsor_type == LEGAL_ENTITY and not self.company_name:
            raise ValidationError({'message': 'Company name is required for legal entities.'})
        if self.sponsor_type == INDIVIDUAL and self.company_name:
            raise ValidationError({'message': 'Individuals should not have company name.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Sponsor, self).save(*args, **kwargs)

    def __str__(self):
        return self.full_name



class StudentSponsor(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    sponsor = models.ForeignKey(Sponsor, on_delete=models.CASCADE)
    allocated_money = models.FloatField(null=False)

    class Meta:
        db_table = 'student_sponsors'
        verbose_name = 'Student sponsor'
        verbose_name_plural = 'Student sponsors'


    def clean(self):
        total_allocated_money_by_sponsor = StudentSponsor.objects.filter(
            sponsor=self.sponsor).exclude(id=self.id).aggregate(total=Sum('allocated_money')
                                                                )['total'] or 0
        remaining_sponsorship_money = self.sponsor.total_sponsorship_amount - total_allocated_money_by_sponsor

        total_allocated_money_for_student = StudentSponsor.objects.filter(
            student=self.student).exclude(id=self.id).aggregate(total=Sum('allocated_money')
                                                                )['total'] or 0
        remaining_tuition_fee = self.student.tuition_fee - total_allocated_money_for_student

        if self.sponsor.status != VERIFIED:
            raise ValidationError(
                {
                    'success': False,
                    'message': 'Unverified sponsor can not allocate money.'
                }
            )

        if remaining_sponsorship_money < self.allocated_money:
            raise ValidationError(
                {
                    'success': False,
                    'message': 'Sponsor does not have enough funds available.'
                }
            )

        if remaining_tuition_fee < self.allocated_money:
            raise ValidationError(
                {
                    'success': False,
                    'message': 'Allocated money exceeds remaining tuition fee.'
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(StudentSponsor, self).save(*args, **kwargs)

    def __str__(self):
        return f"Student {self.student.full_name} - Sponsor {self.sponsor.full_name}"


