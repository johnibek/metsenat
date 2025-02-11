from django.urls import path
from . import views

urlpatterns = [
    path('sponsors/apply', views.SponsorApplicationAPIView.as_view(), name='sponsor_application'),
]