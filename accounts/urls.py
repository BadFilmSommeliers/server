from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token
from .views import ChangePasswordView
from . import views


urlpatterns = [
    path('get-user/', views.get_user),
    path('signup/', views.signup, name='signup'),
    path('api-token-auth/', obtain_jwt_token),
    path('profile/<int:user_pk>/', views.profile),
    path('change_password/<int:pk>/', ChangePasswordView.as_view(), name='auth_change_password'),
    path('get-base-info-for-rec/', views.get_base_info_for_rec, name='get_base_info_for_rec'),
]