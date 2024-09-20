from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    ProtectedView,
    UserListCreateView,
    UserDetailView,
    UserProfileView,
    UserProfileDetailView,
    CreateUserListCreateView,
    CreateUserDetailView,
    ListUsersView,
    LoginUserDetailView,
    LoginUserListCreateView
    )

urlpatterns = [
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('login/', LoginUserDetailView.as_view(), name='login'),
    path('user/', UserListCreateView.as_view(), name='user-list-create'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('userprofile/', UserProfileView.as_view(), name='userprofile-list-create'),
    path('userprofile/<int:pk>/', UserProfileDetailView.as_view(), name='userprofile-detail'),
    path('createuser/', CreateUserListCreateView.as_view(), name='createuser-list-create'),
    path('createuser/<int:pk>/', CreateUserDetailView.as_view(), name='createuser-detail'),
    path('users/',ListUsersView.as_view(), name='all-users'),
    path('loginuser/', LoginUserListCreateView.as_view(), name='loginuser-list-create'),
    path('loginuser/<int:pk>/', LoginUserDetailView.as_view(), name='loginuser-detail'),



]
