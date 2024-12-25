import json
import os
from django.contrib.auth.models import User
from rest_framework import generics, status,permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .serializers import UserSerializers, UserProfileSerializer, CreateUserSerializer,LoginUserSerializer,RegisterSerializer        
from .models import UserProfile, CreateUser ,LoginUser
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate 
from rest_framework.authtoken.models import Token
from django.http import HttpResponse,JsonResponse  
from rest_framework.views import APIView 
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404


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

class ListUsersView(APIView):
    permission_classes = []

    def get(self, request):
        users = User.objects.all().values('id', 'username', 'first_name', 'last_name', 'date_joined')
        return Response(users, status=status.HTTP_200_OK)
    

class LoginUserListCreateView(generics.ListCreateAPIView):
    queryset = LoginUser.objects.all()
    serializer_class = LoginUserSerializer


class LoginUserDetailView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response = Response({
                "access_token": access_token
                
            }, status=status.HTTP_200_OK)

            response['Authorization'] = f'Bearer {access_token}'
            return response
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializers(user)
        return Response(serializer.data)
    
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        first_name = serializer.validated_data.get('first_name')
        last_name = serializer.validated_data.get('last_name')
        email = serializer.validated_data.get('email')  
        password = serializer.validated_data.get('password')

        if User.objects.filter(username=username).exists():
            # Return custom error message in Uzbek
            return Response({
                'error': 'Bunday login ga ega foydalanuvchi allaqachon mavjud.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create the user if the username is not taken
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        try:
            refresh = RefreshToken.for_user(user)
        except Exception as e:
            return Response({
                'detail': f"Error generating token: {str(e)}",
                'code': 'token_error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'access': str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)


# Path to the JSON file
JSON_FILE_PATH = os.path.join(os.path.dirname(__file__), 'combined_data2.json')

# Helper functions to read and write JSON
def read_json():
    with open(JSON_FILE_PATH, "r") as file:
        return json.load(file)

def write_json(data):
    with open(JSON_FILE_PATH, "w") as file:
        json.dump(data, file, indent=4)

# Class-Based View for JSON CRUD operations
@method_decorator(csrf_exempt, name='dispatch')
class ProfessionView(View):
    def get(self, request, profession=None):
        """List all data or a specific profession"""
        data = read_json()  # Ensure read_json is properly implemented to read your JSON file

        if profession:
            if profession in data:
                return JsonResponse(
                    data[profession], 
                    safe=False, 
                    json_dumps_params={'indent': 4}  # Pretty print JSON
                )
            return JsonResponse({"error": "Profession not found"}, status=404)
        
        return JsonResponse(
            data, 
            safe=False, 
            json_dumps_params={'indent': 4}  # Pretty print JSON
        )

    def post(self, request):
        """Add a new branch"""
        data = read_json()
        try:
            profession = request.POST.get("profession")
            branch_data = {
                "id": int(request.POST.get("id")),
                "profession": request.POST.get("profession"),
                "rooms": int(request.POST.get("rooms")),
                "apirarsi_room": int(request.POST.get("apirarsi_room")),
                "responsible_person": request.POST.get("responsible_person"),
                "work_time": request.POST.get("work_time"),
            }
            if profession not in data:
                data[profession] = {"branches": [], "users": []}
            data[profession]["branches"].append(branch_data)
            write_json(data)
            return JsonResponse({"message": "Branch added successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def put(self, request, profession):
        """Update an existing branch"""
        data = read_json()
        if profession not in data:
            return JsonResponse({"error": "Profession not found"}, status=404)

        try:
            branch_id = int(request.POST.get("id"))
            updated_data = {
                "rooms": int(request.POST.get("rooms", 0)),
                "apirarsi_room": int(request.POST.get("apirarsi_room", 0)),
                "responsible_person": request.POST.get("responsible_person"),
                "work_time": request.POST.get("work_time"),
            }
            for branch in data[profession]["branches"]:
                if branch["id"] == branch_id:
                    branch.update(updated_data)
                    write_json(data)
                    return JsonResponse({"message": "Branch updated successfully"})
            return JsonResponse({"error": "Branch not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def delete(self, request, profession):
        """Delete a branch"""
        data = read_json()
        if profession not in data:
            return JsonResponse({"error": "Profession not found"}, status=404)

        try:
            branch_id = int(request.POST.get("id"))
            data[profession]["branches"] = [
                branch for branch in data[profession]["branches"] if branch["id"] != branch_id
            ]
            write_json(data)
            return JsonResponse({"message": "Branch deleted successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class UserView(View):
    def post(self, request, profession):
        """Add a new user to a profession"""
        data = read_json()
        if profession not in data:
            return JsonResponse({"error": "Profession not found"}, status=404)

        try:
            user_data = {
                "id": int(request.POST.get("id")),
                "name": request.POST.get("name"),
                "role": request.POST.get("role"),
            }
            data[profession]["users"].append(user_data)
            write_json(data)
            return JsonResponse({"message": "User added successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
# Create your views here.