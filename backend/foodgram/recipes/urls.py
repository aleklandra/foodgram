from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, IngredientsViewSet, TagsViewSet

v1_router = DefaultRouter()


v1_router.register('recipes', RecipeViewSet)
v1_router.register('tags', TagsViewSet)
v1_router.register('ingredients', IngredientsViewSet)


urlpatterns = [
    path('', include(v1_router.urls)),
]
