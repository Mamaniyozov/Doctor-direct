from django.contrib.auth.models import User
from rest_framework import generics, status,permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .serializers import UserSerializers, UserProfileSerializer, CreateUserSerializer
from .models import UserProfile, CreateUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.http import HttpResponse,JsonResponse  
from rest_framework.views import APIView 


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'This is a protected view!'}
        return Response(content)

class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializers
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        response_data = {
            'user': serializer.data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'is_admin': user.is_staff,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializers



class UserProfileView(generics.CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = UserProfile.objects.get(id=response.data['id'])
        token, created = Token.objects.get_or_create(user=user.user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'access_token': token.key,
            'is_admin': user.user.is_staff,
        })

class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'user': serializer.data,
            'access_token': Token.objects.get(user=instance.user).key,
            'is_admin': instance.user.is_staff,
        })


class CreateUserListCreateView(generics.ListCreateAPIView):
    queryset = CreateUser.objects.all()
    serializer_class = CreateUserSerializer


class CreateUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CreateUser.objects.all()
    serializer_class = CreateUserSerializer


# Create your views here.
