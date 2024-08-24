from django.db import models
from django.core.validators import MinValueValidator
from user.models import User


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
    cooking_time = models.IntegerField(verbose_name='Время приготовления',
                                       validators=[MinValueValidator(1), ])
    image = models.ImageField(upload_to='recipes/images/')
    tags = models.ManyToManyField(Tag, through='TagRecipe')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe',
                                         related_name='ingredients')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name', )


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ingredient')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.IntegerField(verbose_name='Количество в рецепте')

    def __str__(self):
        return f'{self.ingredient} {self.recipe} {self.amount}'


class UserRecipeLists(models.Model):
    recipe = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_favorited = models.BooleanField()
    is_in_shopping_cart = models.BooleanField()

    def __str__(self):
        return f'{self.user} {self.recipe}'
