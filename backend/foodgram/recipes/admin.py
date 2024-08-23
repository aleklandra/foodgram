from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
from recipes.models import Tag, Ingredient, TagRecipe, Recipe, IngredientRecipe
from foodgram.forms import TagForm


admin.site.empty_value_display = 'Не задано'

FORM={
        models.CharField: {'widget': TextInput(attrs={'size':'10'})},
        models.TextField: {'widget': Textarea(attrs={'rows':1, 'cols':30})},
    }


class RecipeInline(admin.StackedInline):
    model = TagRecipe
    extra = 0


class IngredientsInline(admin.StackedInline):
    model = IngredientRecipe
    extra = 0


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
        'author'

    )
    list_editable = (
        'name',
        'text',
        'cooking_time',
        'image',
        'author'
    )
    inlines = (
        IngredientsInline,
        RecipeInline
    )
    search_fields = ('name', 'author' )
    list_filter = ('name', 'author' )
    list_display_links = ('id',)
