from django_filters import rest_framework as filter
from rest_framework import filters

from .models import Recipe, Tag


class RecipeFilter(filter.FilterSet):
    tags = filter.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
        conjoined=False)
    author = filter.CharFilter(field_name='author__id', lookup_expr='exact')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', ]


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'
