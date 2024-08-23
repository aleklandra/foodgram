"""Сериализаторы для работы с пользователем."""
import base64
from collections import OrderedDict
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from djoser.serializers import UserSerializer


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Image conversion."""

    def to_internal_value(self, data):
        """Image conversion class function."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, use_url=True)

    class Meta:
        model = User
        fields = ('avatar', )
    
    def update(self, instance, validated_data):
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.save()
        return instance


class CustomUserSerializer(UserSerializer):
    email = serializers.EmailField(
        required=True,
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        required=True,
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]

    )
    first_name = serializers.CharField(
        required=True,
        max_length=150
    )
    last_name = serializers.CharField(
        required=True,
        max_length=150
    )

    avatar = serializers.SerializerMethodField(
        'get_avatar_url',
        read_only=True,
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password', 'avatar')
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_avatar_url(self, obj):
        """Avatar function."""
        if self.context['request'].path != '/api/users/' and obj.avatar:
            return obj.avatar.url
        return None
    
    def to_representation(self, instance):
        result = super(CustomUserSerializer, self).to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])

