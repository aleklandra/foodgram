from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .models import (Ingredient, Tag, Recipe)
from .serializers import (IngredientsSerializer, TagsSerializer,
                          RecipeSerializer, RecipeListSerializer)
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,)
from rest_framework import filters, status, mixins


class IngredientsViewSet(mixins.ListModelMixin,
                         GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class TagsViewSet(mixins.ListModelMixin,
                  GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeSerializer
