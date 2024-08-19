from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    license_front_image = serializers.ImageField(required=True)
    license_back_image = serializers.ImageField(required=True)

    class Meta:
        model = User
        fields = ('email', 'fname', 'lname', 'gender', 'phone', 'license_no', 'password', 'license_front_image', 'license_back_image')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_phone(self, value):
        phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
        phone_regex(value)
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in value):
            raise ValidationError("Password must contain at least one numeral.")
        if not any(char.isalpha() for char in value):
            raise ValidationError("Password must contain at least one letter.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            fname=validated_data['fname'],
            lname=validated_data['lname'],
            gender=validated_data['gender'],
            phone=validated_data['phone'],
            license_no=validated_data['license_no'],
            password=validated_data['password'],
            license_front_image=validated_data['license_front_image'],
            license_back_image=validated_data['license_back_image'],
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ProfilePictureUpdateSerializer(serializers.Serializer):
    profile_picture = serializers.ImageField()
