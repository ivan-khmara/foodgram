from django.contrib import admin

from .models import (Ingredient, IngredientForRecipe, Recipe, Subscription,
                     Tag, User)

EMPTY_VALUE_DISPLAY = '-пусто-'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'email', 'username', 'first_name', 'last_name',
                    'is_staff',)
    search_fields = ('username', 'email',)
    list_filter = ('username', 'email',)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name',)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(IngredientForRecipe)
class IngredientForRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'ingredient', 'amount')
    search_fields = ('ingredient',)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    fields = ('author', 'tags', 'name', 'image', 'ingredients', 'text',
              'cooking_time',)
    list_display = ('pk', 'author', 'name', 'get_tags', 'get_favorited',)
    list_filter = ('tags', 'author', 'name',)
    search_fields = ('tags', 'author', 'name',)
    empty_value_display = EMPTY_VALUE_DISPLAY

    def get_tags(self, obj):
        return ',\n'.join([p.name for p in obj.tags.all()])

    def get_favorited(self, obj):
        return str(obj.fans.count())


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user',)
    list_filter = ('user', 'author',)
    empty_value_display = EMPTY_VALUE_DISPLAY
