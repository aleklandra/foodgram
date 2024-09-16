from rest_framework import mixins
from recipes.models import Recipe


class FilterModelMixin(mixins.ListModelMixin):
    def get_queryset(self):
        queryset = Recipe.objects.all()
        author = self.request.query_params.getlist('author')
        user = self.request.user
        if author != []:
            queryset_author = Recipe.objects.filter(author__in=author)
        else:
            queryset_author = queryset
        tags = self.request.query_params.getlist('tags')
        if tags != []:
            queryset_tag = Recipe.objects.filter(tags__slug__in=tags)
        else:
            queryset_tag = queryset

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart == '1':
            queryset_shop = (user.recipes_list
                             .filter(is_in_shopping_cart=True)
                             .values('recipe'))
        elif is_in_shopping_cart == '0':
            queryset_shop = (user.recipes_list
                             .filter(is_in_shopping_cart=True)
                             .values('recipe'))
            queryset_shop = queryset.exclude(id__in=queryset_shop)
        else:
            queryset_shop = queryset
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited == '1':
            queryset_fav = (user.recipes_list
                            .filter(is_favorited=True)
                            .values('recipe'))
        elif is_favorited == '0':
            queryset_fav = (user.recipes_list
                            .filter(is_favorited=True)
                            .values('recipe'))
            queryset_fav = queryset.exclude(id__in=queryset_fav)
        else:
            queryset_fav = queryset

        return (queryset.filter(id__in=queryset_shop)
                        .filter(id__in=queryset_fav)
                        .filter(id__in=queryset_tag)
                        .filter(id__in=queryset_author))
