"""Сериализаторы для работы с рецептами."""
import base64
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django_url_shortener.utils import shorten_url
from rest_framework import serializers
from recipes.models import (Tag, Ingredient, Recipe, TagRecipe,
                            IngredientRecipe,
                            UserRecipeLists)
from user.serializers import CustomUserSerializer


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
        for tag in data:
            try:
                tag = Tag.objects.get(pk=tag)
                tags.append(tag)
            except Tag.DoesNotExist:
                raise serializers.ValidationError(f'{id} - такого тега '
                                                  f'не существует')
        return tags


class IngredientsConvertSerializer(serializers.ListField):

    def to_representation(self, value):
        ingredients = []
        ingrs = self.context['request'].data['ingredients']
        amounts = {}
        for ingr in ingrs:
            amounts[ingr['id']] = ingr['amount']
        if value is None:
            return None
        else:
            for val in value.all():
                ingredient = {
                    'id': vars(val)['id'],
                    'name': vars(val)['name'],
                    'measurement_unit': vars(val)['measurement_unit'],
                    'amount': amounts[vars(val)['id']]}
                ingredients.append(ingredient)
            return ingredients

    def to_internal_value(self, data):
        ingredients = []
        for ingredient in data:
            try:
                ingredient_obj = Ingredient.objects.get(pk=ingredient['id'])
                ingredients.append({'ingredient': ingredient_obj,
                                    'amount': ingredient['amount']})
            except Ingredient.DoesNotExist:
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
        ingredients = validated_data.pop('ingredients')
        user = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data, author=user)
        for tag in tags:
            TagRecipe.objects.create(tag=tag, recipe=recipe)
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                ingredient=ingredient['ingredient'],
                recipe=recipe, amount=ingredient['amount'])
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe, status = Recipe.objects.update_or_create(
            pk=instance.id,
            defaults={**validated_data})
        TagRecipe.objects.filter(recipe=instance.id, ).delete()
        IngredientRecipe.objects.filter(recipe=instance.id, ).delete()
        for tag in tags:
            TagRecipe.objects.create(tag=tag, recipe=recipe)
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                ingredient=ingredient['ingredient'],
                recipe=recipe, amount=ingredient['amount'])
        return recipe


class RecipeListSerializer(serializers.ModelSerializer):
    """Recipe."""
    image = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )
    tags = TagsSerializer(many=True,)
    ingredients = IngredientsSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField(
        'get_is_favorited',
        read_only=True,
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart',
        read_only=True,
    )
    author = CustomUserSerializer()

    class Meta:
        """Meta class."""

        model = Recipe
        fields = ('id', 'ingredients', 'tags', 'image', 'name',
                  'text', 'cooking_time', 'is_favorited', 'author',
                  'is_in_shopping_cart')
        read_only_field = ('id', 'author', 'is_favorited',
                           'is_in_shopping_cart')

    def get_image_url(self, obj):
        """Image function."""
        if obj.image:
            return obj.image.url
        return None

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        recipe = UserRecipeLists.objects.filter(user=user, recipe=obj,
                                                is_favorited=True)
        if recipe.count() == 0:
            return False
        return True

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        recipe = UserRecipeLists.objects.filter(user=user, recipe=obj,
                                                is_in_shopping_cart=True)
        if recipe.count() == 0:
            return False
        return True

    def to_representation(self, instance):
        result = super(RecipeListSerializer, self).to_representation(instance)
        for ingr in result['ingredients']:
            ingr.update(IngredientRecipe.objects.values('amount').get(
                recipe=instance,
                ingredient_id=ingr['id']))
        return result


class GetLinkRecipeSerializer(serializers.HyperlinkedModelSerializer):
    short_link = serializers.HyperlinkedIdentityField(
        view_name='recipe-detail')

    class Meta:
        model = Recipe
        fields = ('short_link', )
        read_only_fields = ('short_link', )

    def to_representation(self, instance):
        result = super(GetLinkRecipeSerializer,
                       self).to_representation(instance)
        created, short_url = shorten_url(result['short_link'])
        return {'short-link': short_url}


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )

    class Meta:
        """Meta class."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', )
        read_only_field = ('id', 'name', 'image', 'cooking_time', )

    def get_image_url(self, obj):
        """Image function."""
        if obj.image:
            return obj.image.url
        return None


class DownloadShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        """Meta class."""
        model = Recipe
