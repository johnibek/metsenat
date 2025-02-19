from django.urls import path
from . import views


urlpatterns = [
    path('sponsors/', views.SponsorListAPIView.as_view(), name='sponsor_list'),
    path('sponsors/<uuid:id>', views.SponsorDetailUpdateDeleteAPIView.as_view(), name='sponsor_detail_update_delete'),
    path('students/', views.StudentListCreateAPIView.as_view(), name='student_list_create'),
    path('students/<uuid:id>/', views.StudentDetailUpdateDeleteAPIView.as_view(), name='student_detail_update_delete'),
    path('students/<uuid:student_id>/sponsors/', views.StudentSponsorListCreate.as_view(), name="student_sponsor_list_create"),
    path('students/<uuid:student_id>/sponsors/<uuid:sponsor_id>/', views.StudentSponsorDetailUpdateDeleteAPIView.as_view(), name='student_sponsor_detail_update_delete'),
    path('summary/', views.StudentSponsorSummaryAPIView.as_view(), name='student_sponsor_summary')
]