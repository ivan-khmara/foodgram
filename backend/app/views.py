# from api_yamdb.settings import EMAIL_ADRESS
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
import json
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, mixins, permissions, status,
                            viewsets)
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Tag, Ingredient, Recipe, Subscription, IngredientForRecipe

from .paginations import RecipePagination
from .permissions import (AdminModeratorAuthorOrReadOnly, IsAdminOnly,
                          IsAdminOrReadOnly)
from .serializers import (UserSerializer, TagSerializer, IngredientSerializer, RecipeSerializer,
                          RecipeSerializerPost,
#                         DownloadShoppingSerializer,
                          ShoppingCartSerializer,
                          FavoriteSerializer,
                          SubscriptionsSerializer,
                          SubscribetSerializer
                          )
from drf_yasg.utils import swagger_serializer_method, swagger_auto_schema


# from .filters import TitleFilter

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET     /tags/       - Cписок тегов
    GET     /tags/{id}/  - Получение тега
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET     /ingredients/      - Список ингредиентов
    GET     /ingredients/{id}/ - Получение ингредиента
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """
    GET     /recipes/       - Список рецептов
    POST    /recipes/       - Создание рецепта
    GET     /recipes/{id}/  - Получение рецепта
    PATCH   /recipes/{id}/  - Обновление рецепта
    DEL     /recipes/{id}/  - Удаление рецепта
    """
    queryset = Recipe.objects.all()
    pagination_class = RecipePagination


    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RecipeSerializerPost
        return RecipeSerializer


# class DownloadShoppingCartViewSet():
#     #  GET    /recipes/download_shopping_cart/  Список покупок
#
# class ShoppingCartViewSet():
#     CreateAPIView
#     DestroyAPIView
#     #  POST   /recipes/{id}/shopping_cart/      Добавить рецепт в список покупок
#     #  DEL    /recipes/{id}/shopping_cart/      Удалить рецепт из списка покупок
#
# class FavoriteViewSet():
#     CreateAPIView
#     DestroyAPIView
#     #  POST   /recipes/{id}/favorite/          Добавить рецепт в избранное
#     #  DEL    /recipes/{id}/favorite/          Удалить рецепт из избранного
#


class SubscribetViewSet(mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """
    POST   /users/{id}/subscribe/ - Подписаться на пользователя
    DEL    /users/{id}/subscribe/ - Отписаться от пользователя
    """
    serializer_class = SubscribetSerializer
    queryset = Subscription.objects.all()

    @action(methods=['delete'], detail=False)
    def delete(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        author = get_object_or_404(User, pk=user_id)
        try:
            tmp = get_object_or_404(Subscription, user=request.user, author=author)
            tmp.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            message = 'Вы не были подписаны на автора ' + str(author.username)
            return Response({'errors': message}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        author = get_object_or_404(User, pk=user_id)
        if author == request.user:
            return Response({'errors': 'Подписка на себя не возможна'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            get_object_or_404(Subscription, user=request.user, author=author)
            message = 'Вы уже подписаны на автора ' + str(author.username)
            return Response({'errors': message}, status=status.HTTP_400_BAD_REQUEST)
        except:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=self.request.user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubscriptionsViewSet(mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """
    GET   /users/subscriptions/ - Мои подписки
    """
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        tmp = user.follower.all().order_by('author_id')
        return [i.author for i in tmp]


class ShoppingCartViewSet(mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    """
    POST  http://localhost/api/recipes/{recipe_id}/shopping_cart/ - Добавить рецепт в список покупок
    DEL   http://localhost/api/recipes/{recipe_id}/shopping_cart/ - Удалить рецепт из списка покупок
    """
    serializer_class = ShoppingCartSerializer
    queryset = Recipe.objects.all()

    @action(methods=['delete'], detail=False)
    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if request.user in recipe.is_in_shopping_cart.all():
            recipe.is_in_shopping_cart.remove(request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт не был в списке покупок'}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if request.user in recipe.is_in_shopping_cart.all():
            return Response({'errors': 'Рецепт уже есть в списке покупок'}, status=status.HTTP_400_BAD_REQUEST)
        recipe.is_in_shopping_cart.add(request.user)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FavoriteViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """
    POST   http://localhost/api/recipes/{recipe_id}/favorite/ - Добавить рецепт в избранное
    DEL    http://localhost/api/recipes/{recipe_id}/favorite/ - Удалить рецепт из избранного
    """

    serializer_class = FavoriteSerializer
    queryset = Recipe.objects.all()

    @action(methods=['delete'], detail=False)
    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if request.user in recipe.is_favorited.all():
            recipe.is_favorited.remove(request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт не был в избранном'}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if request.user in recipe.is_favorited.all():
            return Response({'errors': 'Рецепт уже есть в избранном'}, status=status.HTTP_400_BAD_REQUEST)
        recipe.is_favorited.add(request.user)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
