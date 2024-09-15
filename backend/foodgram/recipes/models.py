from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

MAX_VALIDATOR = 32000
MIN_VALIDATOR = 1


User = get_user_model()


class Tag(models.Model):
    name = models.TextField(verbose_name='Название', max_length=32)
    slug = models.SlugField(verbose_name='Уникальный слаг', max_length=32)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name', )

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    name = models.TextField(verbose_name='Название', max_length=128)
    measurement_unit = models.CharField(verbose_name='Единицы измерения',
                                        max_length=64)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name', )

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    name = models.TextField(verbose_name='Название', max_length=256)
    text = models.TextField(verbose_name='Описание', max_length=256)
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(MIN_VALIDATOR),
                    MaxValueValidator(MAX_VALIDATOR)])
    image = models.ImageField(upload_to='recipes/images/',
                              verbose_name='Изображение')
    tags = models.ManyToManyField(Tag, through='TagRecipe')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe',
                                         related_name='recipes',
                                         related_query_name='recipe',
                                         verbose_name='Ингредиенты',
                                         default='Не указан',)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор')
    users = models.ManyToManyField(User,
                                   through='UserRecipeLists',
                                   related_name='user_lists',
                                   related_query_name='recipe',
                                   verbose_name='Подписчики')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name', )

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE,
                            verbose_name='Название')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Идентификатор')

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        ordering = ('tag', )

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ingredient',
                                   verbose_name='Ингредиент',)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_ingredients',
                               verbose_name='Рецепт')
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество в рецепте',
        validators=[MinValueValidator(MIN_VALIDATOR),
                    MaxValueValidator(MAX_VALIDATOR)])

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        ordering = ('ingredient', )

    def __str__(self):
        return f'{self.ingredient} {self.recipe} {self.amount}'


class UserRecipeLists(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='user_recipe',
                               verbose_name='Рецепт')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='recipes_list',
                             verbose_name='Подписчик')
    is_favorited = models.BooleanField(default=False,
                                       verbose_name='В избранном')
    is_in_shopping_cart = models.BooleanField(default=False,
                                              verbose_name='В списоке покупок')

    class Meta:
        verbose_name = 'В избранном у пользователя'
        verbose_name_plural = 'В избранном у пользователей'

    def __str__(self):
        return f'{self.user} {self.recipe}'
