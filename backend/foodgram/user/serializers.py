"""Сериализаторы для работы с пользователем."""
import base64

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from user.models import UserSubscription

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
        instance.avatar = validated_data.get('avatar', instance.avatar)
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
    is_subscribed = serializers.SerializerMethodField(
        'get_is_subscribed',
        read_only=True,
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password',
                  'avatar', 'id', 'is_subscribed', 'recipes', 'recipes_count')
        extra_kwargs = {'password': {'write_only': True}, }

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
        if obj.avatar:
            return obj.avatar.url
        return None

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return user.user_person.filter(sub_id=obj).exists()


class SubscribtionListSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(
        'get_recipes',
        read_only=True,
    )
    recipes_count = serializers.SerializerMethodField(
        'get_recipes_count',
        read_only=True,
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name',
                  'avatar', 'id', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.values('id',
                                     'name',
                                     'image',
                                     'cooking_time').all()[:limit]
        for recipe in recipes:
            recipe['image'] = settings.MEDIA_URL + recipe['image']
        return recipes

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()


class SubscribtionCreateSerializer(serializers.ModelSerializer):
    person_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all())
    sub_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all())

    class Meta:
        fields = '__all__'
        model = UserSubscription
        validators = [
            UniqueTogetherValidator(
                queryset=UserSubscription.objects.all(),
                fields=['sub_id', 'person_id'],
                message='Вы уже подписаны на данного человека'
            )
        ]

    def validate(self, data):
        user = data['person_id']
        current_sub = data['sub_id']
        if user == current_sub:
            raise serializers.ValidationError(
                ['Подписка на себя невозможна'])
        return data

    def update(self, instance, validated_data):
        instance.delete()
        return
