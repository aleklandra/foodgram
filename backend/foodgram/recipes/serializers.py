"""Сериализаторы для работы с рецептами."""
import base64
from collections import OrderedDict
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from .models import Tag, Ingredient, Recipe, TagRecipe, IngredientRecipe


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


class TagsConvertSerializer(serializers.ListField):

    def to_representation(self, value):
        tags = []
        if value is None:
            return None
        else:
            for val in value.all():
                tag = {'id': vars(val)['id'],
                       'name': vars(val)['name'],
                       'slug': vars(val)['slug']}
                tags.append(tag)
            return tags

    def to_internal_value(self, data):
        tags = []
        for id in data:
            try:
                tag = Tag.objects.get(pk=id)
                tags.append(tag)
            except Tag.DoesNotExist:
                raise serializers.ValidationError(f'{id} - такого тега '
                                                  f'не существует')
        return tags


class IngredientsConvertSerializer(serializers.ListField):

    def to_representation(self, value):
        ingredients = []
        if value is None:
            return None
        else:
            for val in value.all():
                ingredient = { 'id': vars(val)['id'],
                               'name': vars(val)['name'],
                               'measurement_unit': vars(val)['measurement_unit'],
                               'amount': vars(val)['amount']}
                ingredients.append(ingredient)
            return ingredients

    def to_internal_value(self, data):
        ingredients = []
        for id in data:
            try:
                ingredient = Tag.objects.get(pk=id)
                ingredients.append(ingredient)
            except Tag.DoesNotExist:
                raise serializers.ValidationError(f'{id} - такого ингредиента '
                                                  f'не существует')
        return ingredients


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientsConvertSerializer()
    tags = TagsConvertSerializer()
    image = Base64ImageField(required=False, allow_null=True)
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name',
                  'text', 'cooking_time', 'id', 'author')
        read_only_field = ('id', 'author')

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('category')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            TagRecipe.objects.create(tag=tag, recipe=recipe)
        for ingredient in ingredients:
            IngredientRecipe.objects.create(ingredient=ingredient['id'], recipe=recipe, amount=ingredient['amount'])
        return recipe


class IngredientRecipeSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField(
        'get_amount',
        read_only=True,
    )
    class Meta:
        """Meta class."""

        model = Ingredient
        fields = ('id', 'name', 'amount', 'measurement_unit')

    def get_amount(self, obj):
        """Image function."""
        ingred = IngredientRecipe.objects.get(ingredient=obj)
        return ingred.amount


class RecipeListSerializer(serializers.ModelSerializer):
    """Recipe."""
    image = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )
    tags = TagsSerializer(many=True,)
    ingredients = IngredientRecipeSerializer(many=True, )

    class Meta:
        """Meta class."""

        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name',
                  'text', 'cooking_time', 'id')
        read_only_field = ('id', 'author')

    def get_image_url(self, obj):
        """Image function."""
        if obj.image:
            return obj.image.url
        return None
