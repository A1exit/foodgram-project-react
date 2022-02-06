from django_filters import AllValuesMultipleFilter, BooleanFilter, FilterSet
from django_filters import rest_framework as filters
from django_filters.widgets import BooleanWidget

from .models import Recipe


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class RecipeFilter(FilterSet):
    is_favorited = BooleanFilter(method="filter_is_favorited",
                                 widget=BooleanWidget())
    in_shopping_cart = BooleanFilter(method="filter_is_favorited",
                                     widget=BooleanWidget())
    tags = AllValuesMultipleFilter(field_name='tags__slug')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(favorites__user=user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(shopping_cart__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['tags__slug', 'is_favorited', 'in_shopping_cart']
