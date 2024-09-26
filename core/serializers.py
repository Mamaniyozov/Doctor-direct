from.models import UserProfile, CreateUser,LoginUser
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField       
from django.contrib.auth.models import User


from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializers(ModelSerializer):
    access_token = SerializerMethodField()
    is_admin = SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'access_token', 'is_admin']

    def get_access_token(self, obj):
        refresh = RefreshToken.for_user(obj)
        return str(refresh.access_token)

    def get_is_admin(self, obj):
        return obj.is_staff


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class CreateUserSerializer(ModelSerializer):
    access_token = SerializerMethodField()

    class Meta:
        model = CreateUser
        fields = "__all__"

    def create(self, validated_data):
        # Create the user
        user = User.objects.create_user(
            username=validated_data['name'],
            first_name=validated_data['firstname'],
            last_name=validated_data['lastname'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        # Create the CreateUser instance
        create_user = CreateUser.objects.create(user=user, **validated_data)
        return create_user

    def get_access_token(self, obj):
        refresh = RefreshToken.for_user(obj.user)
        return str(refresh.access_token)
    
class LoginUserSerializer(ModelSerializer):
    class Meta:
        model = LoginUser
        fields = ['username', 'password']  # Only include the username and password fields

    def validate(self, data):
        if 'email' in data:
            raise serializers.ValidationError("Login with email is not allowed.")
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'username']
        extra_kwargs = {
            'username': {
                'validators': []  # Disable the default unique validator
            }
        }

    def validate_username(self, value):
        # Custom username validation
        if User.objects.filter(username=value).exists():
            # Return the custom error message in Uzbek
            raise serializers.ValidationError("Bunday login ga ega foydalanuvchi allaqachon mavjud.")
        return value

    def create(self, validated_data):
        # Create a new user with the validated data
        user = User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            username=validated_data['username'],
            email=validated_data['email'],
        )
        return user
