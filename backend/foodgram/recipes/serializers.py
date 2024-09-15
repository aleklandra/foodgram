import base64
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (Ingredient, IngredientRecipe, Recipe, Tag,
                            TagRecipe)
from user.serializers import CustomUserSerializer

MAX_VALUE = 32000
MIN_VALUE = 1

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


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsRecipeSerializer(serializers.ModelSerializer):

    amount = serializers.IntegerField(max_value=MAX_VALUE, min_value=MIN_VALUE)
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        depth = 1
        fields = ('id', 'amount', 'name', 'measurement_unit')


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
        read_only_field = ('name', 'slug')

    def to_internal_value(self, data):
        try:
            tag = Tag.objects.get(pk=data)
        except Tag.DoesNotExist:
            raise serializers.ValidationError(f'{id} - такого тега '
                                              f'не существует')
        return tag


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientsRecipeSerializer(many=True,
                                              source='recipe_ingredients')
    tags = TagsSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True)
    cooking_time = serializers.IntegerField(max_value=MAX_VALUE,
                                            min_value=MIN_VALUE)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name',
                  'text', 'cooking_time', 'id', 'author')
        read_only_field = ('id', 'author')

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        user = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data, author=user)
        self.tags_create(tags, recipe)
        self.ingredients_create(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        recipe, status = Recipe.objects.update_or_create(
            pk=instance.id,
            defaults={**validated_data})
        TagRecipe.objects.filter(recipe=instance.id, ).delete()
        IngredientRecipe.objects.filter(recipe=instance.id, ).delete()
        self.tags_create(tags, recipe)
        self.ingredients_create(ingredients, recipe)
        return recipe

    def ingredients_create(self, ingredients, recipe):
        ingredients_array = []
        for ingredient in ingredients:
            ingredients_array.append(IngredientRecipe(
                ingredient=get_object_or_404(
                    Ingredient,
                    pk=ingredient['ingredient']['id']),
                recipe=recipe, amount=ingredient['amount']))
        IngredientRecipe.objects.bulk_create(ingredients_array)

    def tags_create(self, tags, recipe):
        tags_array = []
        for tag in tags:
            tags_array.append(TagRecipe(tag=tag, recipe=recipe))
        TagRecipe.objects.bulk_create(tags_array)


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
        return user.recipes_list.filter(recipe=obj, is_favorited=True).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return (user.recipes_list.filter(recipe=obj, is_in_shopping_cart=True)
                .exists())

    def to_representation(self, instance):
        result = super(RecipeListSerializer, self).to_representation(instance)
        for ingr in result['ingredients']:
            ingr.update(IngredientRecipe.objects.values('amount').get(
                recipe=instance,
                ingredient_id=ingr['id']))
        return result


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
