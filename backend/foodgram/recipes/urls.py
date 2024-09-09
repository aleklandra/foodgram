from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import IngredientsViewSet, RecipeViewSet, TagsViewSet

v1_router = DefaultRouter()


v1_router.register('recipes', RecipeViewSet)
v1_router.register('tags', TagsViewSet)
v1_router.register('ingredients', IngredientsViewSet)


urlpatterns = [
    path('', include(v1_router.urls)),
]
