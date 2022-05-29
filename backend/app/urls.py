from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (TagViewSet, IngredientViewSet, RecipeViewSet,
#                    DownloadShoppingCartViewSet, ShoppingCartViewSet, FavoriteViewSet, SubscriptionsViewSet, SubscribetViewSet, UserNameViewSet,
                    UserViewSet, GetConfirmationCodeView, GetTokenApiView)

router = DefaultRouter()

router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

# router.register('recipes/download_shopping_cart', DownloadShoppingCartViewSet, basename='download_shopping_cart')
# router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart', ShoppingCartViewSet, basename='shopping_cart')
# router.register(r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet, basename='favorite')

router.register('users', UserViewSet)
# router.register('users/subscriptions', SubscriptionsViewSet, basename='subscriptions')
# router.register(r'users/(?P<user_id>\d+)/subscribe', SubscribetViewSet, basename='subscribe')


urlpatterns = [
    path('', include(router.urls)),
    # path('/auth/signup/', GetConfirmationCodeView.as_view()),
    # path('/auth/token/', GetTokenApiView.as_view()),
]
