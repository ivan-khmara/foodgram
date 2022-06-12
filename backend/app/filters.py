from django_filters import rest_framework as filter
from .models import Recipe


class RecipeFilter(filter.FilterSet):
    tags = filter.CharFilter(field_name='tags__slug')
    author = filter.CharFilter(field_name='author__id', lookup_expr='contains')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', ]




