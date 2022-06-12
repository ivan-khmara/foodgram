from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (TagViewSet,
                    IngredientViewSet,
                    RecipeViewSet,
                    DownloadShoppingCart,
                    ShoppingCartViewSet,
                    FavoriteViewSet,
                    SubscriptionsViewSet,
                    SubscribetViewSet,
                    )

router = DefaultRouter()


router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart', ShoppingCartViewSet, basename='shopping_cart')
router.register(r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet, basename='favorite')
router.register(r'users/subscriptions', SubscriptionsViewSet, basename='subscriptions')
router.register(r'users/(?P<user_id>\d+)/subscribe', SubscribetViewSet, basename='subscribe')

urlpatterns = [
    path('recipes/download_shopping_cart/', DownloadShoppingCart.as_view()),
    path('', include(router.urls)),
]
