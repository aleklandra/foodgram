import io
from os import path

from django.db.models import F, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import NoReverseMatch
from django_url_shortener.utils import shorten_url
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from recipes.mixins import FilterModelMixin
from recipes.models import (Ingredient, Recipe, Tag, UserRecipeLists)
from recipes.permissions import IsAuthorOrAdminOrReadOnly
from recipes.serializers import (DownloadShoppingCartSerializer,
                                 FavoriteRecipeSerializer,
                                 IngredientsSerializer, RecipeListSerializer,
                                 RecipeSerializer, TagsSerializer)

TEXT_ORIGIN_SIZE = 10.8
FONT_SIZE = 16


class IngredientsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                         GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)
    pagination_class = None


class TagsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                  GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipeViewSet(ModelViewSet, FilterModelMixin):
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        detail=True,
        methods=('get', ),
        permission_classes=(IsAuthenticatedOrReadOnly, ),
        url_path='get-link'
    )
    def get_link(self, request, pk):
        get_object_or_404(Recipe, id=pk)
        try:
            _, short_link = shorten_url(
                request.build_absolute_uri('/recipes/' + pk))
        except NoReverseMatch:
            return Response({'detail': 'Не найдено'},
                            status=status.HTTP_404_NOT_FOUND)
        return Response({'short-link': short_link},
                        status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated, ),
        url_path='favorite'
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_fav, created = UserRecipeLists.objects.get_or_create(
            recipe=recipe,
            user=request.user,
            is_favorited=True)
        if request.method == 'POST':
            if created is True:
                serializer = self.get_serializer(recipe)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'errors': 'Рецепт уже добавлен в избранное'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            recipe_fav.delete()
            if created is True:
                return Response({
                    'errors': 'Рецепт не был ранее добавлен в избранное'},
                    status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated, ),
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_fav, created = UserRecipeLists.objects.get_or_create(
            recipe=recipe,
            user=request.user,
            is_in_shopping_cart=True)
        if request.method == 'POST':
            if created is True:
                serializer = self.get_serializer(recipe)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'errors': 'Рецепт уже добавлен в покупки'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            recipe_fav.delete()
            if created is True:
                return Response({
                    'errors': 'Рецепт не был ранее добавлен в покупки'},
                    status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get', ),
        permission_classes=(IsAuthenticated, ),
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request,):
        ingredients = (
            request.user
            .recipes_list
            .filter(is_in_shopping_cart=True)
            .prefetch_related('recipe__recipe_ingredients')
            .annotate(name=F('recipe__recipe_ingredients__ingredient__name'),
                      measurement_unit=F('recipe__recipe_ingredients__'
                                         'ingredient__measurement_unit'))
            .values('name', 'measurement_unit')
            .annotate(amount=Sum('recipe__recipe_ingredients__amount')))
        if ingredients.exists() is False:
            return Response({'errors': 'В списке покупок пусто'},
                            status=status.HTTP_404_NOT_FOUND)
        else:
            app_path = path.realpath(path.dirname(__file__))
            font_path = path.join(app_path, 'fonts/DejaVuSerif.ttf')
            pdfmetrics.registerFont(TTFont('DejaVuSerif', font_path))
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            textobject = c.beginText()
            textobject.setTextOrigin(inch, TEXT_ORIGIN_SIZE * inch)
            textobject.setFont('DejaVuSerif', FONT_SIZE)
            for ingr in ingredients:
                textobject.textLine(ingr['name'] + ' ('
                                    + ingr['measurement_unit']
                                    + ') - ' + str(ingr['amount']))
            c.drawText(textobject)
            c.showPage()
            c.save()
            buffer.seek(0)
            return FileResponse(buffer, as_attachment=True,
                                filename='shopping_cart.pdf')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        if self.action == 'favorite' or self.action == 'shopping_cart':
            return FavoriteRecipeSerializer
        if self.action == 'download_shopping_cart':
            return DownloadShoppingCartSerializer
        return super().get_serializer_class()
