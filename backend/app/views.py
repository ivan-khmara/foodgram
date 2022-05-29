# from api_yamdb.settings import EMAIL_ADRESS
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, mixins, permissions, status,
                            viewsets)
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Tag, Ingredient, Recipe, Follow, IngredientForRecipe

from .paginations import CommentsSetPagination, ReviewsSetPagination
from .permissions import (AdminModeratorAuthorOrReadOnly, IsAdminOnly,
                          IsAdminOrReadOnly)
from .serializers import (UserSerializer, TagSerializer, IngredientSerializer, RecipeSerializer,
#                         DownloadShoppingSerializer, ShoppingCarSerializer,
#                         FavoriteSerializer, SubscriptionsSerializer,
#                         SubscribetSerializer,
                          UserForAdminSerializer, GetConfirmationCodeSerializer, GetTokenSerializer)
#from .filters import TitleFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    # ListAPIView
    # RetrieveAPIView
    #  GET     /tags/               Cписок тегов
    #  GET     /tags/{id}/          Получение тега

    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    # ListAPIView
    # RetrieveAPIView
    #  GET     /ingredients/        Список ингредиентов
    #  GET     /ingredients/{id}/   Получение ингредиента

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    #  GET     /recipes/           Список рецептов
    #  POST    /recipes/           Создание рецепта
    #  GET     /recipes/{id}/      Получение рецепта
    #  PATCH   /recipes/{id}/      Обновление рецепта
    #  DEL     /recipes/{id}/      Удаление рецепта

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

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
# class SubscriptionsViewSet():
#     #  GET    /users/subscriptions/            Мои подписки
#
# class SubscribetViewSet():
#     CreateAPIView
#     DestroyAPIView
#     #  POST   /users/{id}/subscribe/           Подписаться на пользователя
#     #  DEL    /users/{id}/subscribe/           Отписаться от пользователя



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserForAdminSerializer
    permission_classes = (IsAdminOnly,)
    lookup_field = 'username'
    search_fields = ('=username',)
    pagination_class = PageNumberPagination

    @action(detail=False, methods=['GET', 'PATCH'],
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        if request.method != 'PATCH':
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(
            request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetConfirmationCodeView(APIView):
    http_method_names = ['post', ]
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = GetConfirmationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        if User.objects.filter(username=username).exists():
            message = 'Пользователь с таким username уже существует'
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            message = 'Пользователь с таким email уже существует'
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create(username=username, email=email)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Вы зарегистрировались на ресурсе API.',
            f'Вот ваш код-подтверждение: {confirmation_code}',
            EMAIL_ADRESS,
            (email,),
            fail_silently=False,
        )
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class GetTokenApiView(APIView):
    http_method_names = ['post', ]
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        confirmation_code = serializer.validated_data.get('confirmation_code')
        if default_token_generator.check_token(user, confirmation_code):
            access_token = RefreshToken.for_user(user).access_token
            data = {'token': str(access_token)}
            return Response(data, status=status.HTTP_201_CREATED)
        errors = {'error': 'confirmation code is incorrect'}
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
