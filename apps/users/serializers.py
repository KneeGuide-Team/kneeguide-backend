from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import User, EmailOTP


password_validator = RegexValidator(
    regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).{8,}$',
    message="Password must contain uppercase, lowercase, number, symbol and 8 chars minimum."
)


class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=150, trim_whitespace=True, allow_blank=False)
    last_name = serializers.CharField(max_length=150, trim_whitespace=True, allow_blank=False)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, trim_whitespace=True, allow_blank=False)
    dob = serializers.DateField(required=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    password = serializers.CharField(write_only=True, validators=[password_validator])

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'dob', 'password', 'role']

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def validate(self, attrs):
        attrs['username'] = attrs['email']
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        # المستخدم غير مفعل حتى يتحقق الـ OTP
        user.is_active = False
        user.save()
        return user


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.RegexField(
        r'^\d{6}$',
        error_messages={'invalid': 'Code must contain exactly 6 digits.'},
    )

    def validate_email(self, value):
        return value.strip().lower()


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.strip().lower()


class LoginSerializer(EmailSerializer):
    password = serializers.CharField(trim_whitespace=False)


class UserSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone',
            'dob',
            'age',
            'role',
            'assigned_doctor',
            'last_activity',
        ]
