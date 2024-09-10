"""Настройка админки для управления ресурсами."""

from adminka.forms import TagForm
from django.contrib import admin
from django.db import models
from django.forms import Textarea, TextInput
from recipes.models import (Ingredient, IngredientRecipe, Recipe, Tag,
                            TagRecipe, UserRecipeLists)
from user.models import User

admin.site.empty_value_display = 'Не задано'

FORM = {models.CharField: {'widget': TextInput(attrs={'size': '10'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 1,
                                                     'cols': 30})}, }


class RecipeInline(admin.StackedInline):
    model = TagRecipe
    extra = 0


class IngredientsInline(admin.StackedInline):
    model = IngredientRecipe
    extra = 0


class UserRecipeListsInLine(admin.StackedInline):
    model = UserRecipeLists
    extra = 0


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'avatar',
    )
    list_editable = (
        'first_name',
        'last_name',
        'avatar',
        'username'
    )
    inlines = (
        UserRecipeListsInLine,
    )
    search_fields = ('email', 'username')
    list_display_links = ('email',)


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    form = TagForm
    formfield_overrides = FORM
    list_display = (
        'id',
        'name',
        'slug',
    )
    list_editable = (
        'name',
    )
    inlines = (
        RecipeInline,
    )
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')
    list_display_links = ('slug',)


@admin.register(Ingredient)
class IngredientsAdmin(admin.ModelAdmin):
    formfield_overrides = FORM
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_editable = (
        'measurement_unit',
    )
    search_fields = ('name', )
    list_filter = ('name', )
    list_display_links = ('name',)


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    formfield_overrides = FORM
    list_display = (
        'id',
        'name',
        'text',
        'cooking_time',
        'image',
        'author',
        'author_username',
        'favorite_count'

    )
    list_editable = (
        'name',
        'text',
        'cooking_time',
        'image',
        'author',
    )
    inlines = (
        IngredientsInline,
        RecipeInline,
        UserRecipeListsInLine
    )
    search_fields = ('name', 'author')
    list_filter = ('tags', )
    list_display_links = ('id',)

    def author_username(self, obj):
        return obj.author.username

    def favorite_count(self, obj):
        return UserRecipeLists.objects.filter(recipe=obj,
                                              is_favorited=True).count()

    author_username.short_description = 'Имя автора'
    favorite_count.short_description = 'В избранном'
