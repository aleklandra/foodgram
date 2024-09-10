"""Сериализаторы для работы с пользователем."""
import base64
from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from recipes.models import Recipe
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
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
        try:
            tmp = UserSubscription.objects.get(
                person_id=self.context['request'].user.id,
                sub_id=obj)
        except UserSubscription.DoesNotExist:
            tmp = None
        if tmp is None:
            return False
        else:
            return True

    def get_recipes(self, obj):
        if self.context['request'].path == '/api/users/subscriptions/':
            request = self.context.get('request')
            if request.query_params.get('recipes_limit'):
                count = int(request.query_params.get('recipes_limit'))
            else:
                count = None
            recipes = Recipe.objects.filter(author=obj.id)[:count]
            recipe_list = []
            for recipe in recipes:
                recipe_list.append(
                    {
                        'id': recipe.id,
                        'name': recipe.name,
                        'image': recipe.image.url,
                        'cooking_time': recipe.cooking_time
                    }
                )
            if len(recipe_list) != 0:
                return recipe_list
            else:
                return None
        else:
            return None

    def get_recipes_count(self, obj):
        if self.context['request'].path == '/api/users/subscriptions/':
            recipes = Recipe.objects.filter(author=obj.id).count()
            if recipes is None:
                return 0
            else:
                return recipes
        else:
            return None

    def to_representation(self, instance):
        result = super(CustomUserSerializer, self).to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result
                            if result[key] is not None])
