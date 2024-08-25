from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .models import (Ingredient, Tag, Recipe)
from recipes.serializers import (IngredientsSerializer, TagsSerializer,
                          RecipeSerializer, RecipeListSerializer,
                          GetLinkRecipeSerializer)
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

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        if self.action == 'get-link':
            return GetLinkRecipeSerializer
        return super().get_serializer_class()
