import io
from os import path
import reportlab
from django.http import FileResponse
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from .models import (Ingredient, Tag, Recipe, UserRecipeLists, IngredientRecipe)
from recipes.serializers import (IngredientsSerializer, TagsSerializer,
                          RecipeSerializer, RecipeListSerializer,
                          GetLinkRecipeSerializer,
                          FavoriteRecipeSerializer,
                          DownloadShoppingCartSerializer)
from django.shortcuts import get_object_or_404
from rest_framework.permissions import (IsAuthenticatedOrReadOnly, IsAuthenticated)
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import filters


class IngredientsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                         GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter, )
    pagination_class = None
    search_fields = ('name',)


class TagsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                  GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'tags__slug') 
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        queryset = Recipe.objects.all()
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited is not None:
            is_favorited = int(is_favorited)

        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_in_shopping_cart is not None:
            is_in_shopping_cart = int(is_in_shopping_cart)

        if is_in_shopping_cart == 1:
            queryset_shop = UserRecipeLists.objects.values('recipe').filter(
                is_in_shopping_cart=True,
                user=self.request.user,)
        elif is_in_shopping_cart == 0:
            queryset_shop = UserRecipeLists.objects.values('recipe').filter(
                is_in_shopping_cart=True,
                user=self.request.user,)
            queryset_shop = queryset.exclude(id__in=queryset_shop)
        else:
            queryset_shop = queryset

        if is_favorited == 1:
            queryset_fav = UserRecipeLists.objects.values('recipe').filter(
                is_favorited=True,
                user=self.request.user,)
        elif is_favorited == 0:
            queryset_fav = UserRecipeLists.objects.values('recipe').filter(
                is_favorited=True,
                user=self.request.user,)
            queryset_fav = queryset.exclude(id__in=queryset_fav)
        else:
            queryset_fav = queryset

        queryset = queryset.filter(id__in=queryset_shop).filter(id__in=queryset_fav)
        return queryset

    @action(
        detail=True,
        methods=('get', ),
        permission_classes=(IsAuthenticatedOrReadOnly,),
        url_path='get-link'
    )
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='favorite'
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        try:
            tmp = UserRecipeLists.objects.get(recipe=pk,
                                              user=request.user,)
        except UserRecipeLists.DoesNotExist:
            tmp = None
        if request.method == 'POST':
            if tmp is None or tmp.is_favorited==False:
                UserRecipeLists.objects.update_or_create(
                    id=tmp.id,
                    defaults={'user': request.user,
                              'is_favorited': True,
                              'recipe': recipe})
                serializer = self.get_serializer(recipe)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'errors': 'Рецепт уже добавлен в избранное'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            if tmp is None or tmp.is_favorited==False:
                return Response({'errors': 'Рецепт не был ранее добавлен в избранное'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                UserRecipeLists.objects.update_or_create(
                    id=tmp.id,
                    defaults={'user': request.user,
                              'is_favorited': False,
                              'recipe': recipe})
                return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        try:
            tmp = UserRecipeLists.objects.get(recipe=pk,
                                              user=request.user,)
        except UserRecipeLists.DoesNotExist:
            tmp = None
        if request.method == 'POST':
            if tmp is None or tmp.is_in_shopping_cart==False:
                UserRecipeLists.objects.update_or_create(
                    id=tmp.id,
                    defaults={'user': request.user,
                              'is_in_shopping_cart': True,
                              'recipe': recipe})
                serializer = self.get_serializer(recipe)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'errors': 'Рецепт уже есть в списке покупок'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            if tmp is None or tmp.is_in_shopping_cart==False:
                return Response({'errors': 'Рецепт не был ранее добавлен в список покупок'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                UserRecipeLists.objects.update_or_create(
                    id=tmp.id,
                    defaults={'user': request.user,
                              'is_in_shopping_cart': False,
                              'recipe': recipe})
                return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get', ),
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request,):
        recipes = UserRecipeLists.objects.filter(
            user=request.user,
            is_in_shopping_cart=True
        ).prefetch_related('recipe')
        shopping_cart = {}
        for recipe in recipes:
            ingredients = IngredientRecipe.objects.filter(recipe=recipe.id).select_related('ingredient')
            for ingr in ingredients:
                key = str(ingr.ingredient.name + ' ('+ ingr.ingredient.measurement_unit + ')')
                if key in shopping_cart.keys():
                    shopping_cart[key] += ingr.amount
                else:
                    shopping_cart[key] = ingr.amount
        app_path = path.realpath(path.dirname(__file__))
        font_path = path.join(app_path, 'static/fonts/DejaVuSerif.ttf')
        pdfmetrics.registerFont(TTFont('DejaVuSerif', font_path))
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer,  pagesize=A4)
        textobject = c.beginText()
        textobject.setTextOrigin(inch, 10.8*inch)
        textobject.setFont('DejaVuSerif', 16)
        for ingr in shopping_cart:
            textobject.textLine((ingr + ' - ' + str(shopping_cart[ingr])))
        textobject.setFillGray(0.4)
        c.drawText(textobject)
        c.showPage()
        c.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='shopping_cart.pdf')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        if self.action == 'get-link':
            return GetLinkRecipeSerializer
        if self.action == 'favorite' or self.action == 'shopping_cart':
            return FavoriteRecipeSerializer
        if self.action == 'download_shopping_cart':
            return DownloadShoppingCartSerializer
        return super().get_serializer_class()
