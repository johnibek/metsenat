from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from .views import LoginStaffUserView, LoginRefreshView

urlpatterns = [
    path('signup/', views.SignUpStaffUserAPIView.as_view(), name='signup_staff_user'),  # Superusers create staff users
    path('login/', LoginStaffUserView.as_view(), name='login_staff_user'),
    path('login/refresh/', LoginRefreshView.as_view(), name='login_refresh'),
    path('logout/', views.LogoutStaffUserAPIView.as_view(), name='logout_staff_user'),
    path('user/data/', views.ViewStaffUserDataAPIView.as_view(), name="view_staff_user_data"),  # Viewing own data
    path('user/data/change/', views.ChangeStaffUserDataAPIView.as_view(), name='change_staff_user_data'),  # Changing own data
    path('user/password/change/', views.ChangePasswordAPIView.as_view(), name='change_password'),
]