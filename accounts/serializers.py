from rest_framework import serializers
from .models import LogmanUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogmanUser
        fields = ['id', 'email', 'name', 'is_active', 'is_superuser', 'is_staff', 'organization', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'organization': {'required': False, 'allow_null': True},
        }

    def create(self, validated_data):
        required = ['password', 'name', 'email']
        for field in required:
            if not validated_data.get(field):
                raise serializers.ValidationError({field: "This field is required."})

        password = validated_data.pop('password')
        user = LogmanUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    """Self-service profile: a user may edit only their own name/email."""
    class Meta:
        model = LogmanUser
        fields = ['id', 'email', 'name', 'is_active', 'is_superuser', 'organization']
        read_only_fields = ['id', 'is_active', 'is_superuser', 'organization']


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user





class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # token['name'] = user.name
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        user_groups = self.user.groups.values_list('name', flat=True)
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'name': self.user.name,
            'groups': list(user_groups)
        }
        return data
    
class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = RefreshToken(attrs['refresh'])
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data
