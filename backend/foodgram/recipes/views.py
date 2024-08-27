from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .models import (Ingredient, Tag, Recipe, UserRecipeLists)
from recipes.serializers import (IngredientsSerializer, TagsSerializer,
                          RecipeSerializer, RecipeListSerializer,
                          GetLinkRecipeSerializer,
                          FavoriteRecipeSerializer)
from django.shortcuts import get_object_or_404
from rest_framework.permissions import (IsAuthenticatedOrReadOnly, IsAuthenticated)
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action


class IngredientsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                         GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


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
    http_method_names = ('get', 'post', 'patch', 'delete')

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
                                                        user=request.user,
                                                        is_favorited=True)
        except UserRecipeLists.DoesNotExist:
            tmp = None
        if request.method == 'POST':
            if tmp is None:
                UserRecipeLists.objects.create(
                    user=request.user, is_favorited=True,
                    recipe=recipe)
                serializer = self.get_serializer(recipe)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'errors': 'Рецепт уже добавлен в избранное'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            if tmp is None:
                return Response({'errors': 'Рецепт не был ранее добавлен в избранное'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                UserRecipeLists.objects.update_or_create(
                    id=tmp.id,
                    defaults={'user': request.user,
                              'is_favorited': False,
                              'recipe': recipe})
                return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        if self.action == 'get-link':
            return GetLinkRecipeSerializer
        if self.action == 'favorite':
            return FavoriteRecipeSerializer
        return super().get_serializer_class()
