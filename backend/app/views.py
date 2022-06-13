import io

import reportlab
from django.conf import settings
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import (filters, mixins, status,
                            viewsets)
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import RecipeFilter, IngredientSearchFilter
from .models import User, Tag, Ingredient, Recipe, Subscription, IngredientForRecipe
from .paginations import CustomPagination
from .permissions import IsAuthorOrAuthReadOnly, IsAuthorOrReadOnly
from .serializers import (TagSerializer, IngredientSerializer, RecipeGetSerializer,
                          RecipePostSerializer,
                          RecipeMiniSerializer,
                          SubscriptionsSerializer,
                          SubscribetSerializer
                          )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET     /tags/       - Cписок тегов
    GET     /tags/{id}/  - Получение тега
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [IsAuthorOrReadOnly, ]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET     /ingredients/      - Список ингредиентов
    GET     /ingredients/{id}/ - Получение ингредиента
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    filter_backends = [IngredientSearchFilter]
    search_fields = ['name']
    permission_classes = [IsAuthorOrReadOnly, ]


class RecipeViewSet(viewsets.ModelViewSet):
    """
    GET      http://localhost/api/recipes/       - Список рецептов
    POST     http://localhost/api/recipes/       - Создание рецепта
    GET      http://localhost/api/recipes/{id}/  - Получение рецепта
    PATCH    http://localhost/api/recipes/{id}/  - Обновление рецепта
    DEL      http://localhost/api/recipes/{id}/  - Удаление рецепта
    GET      http://localhost/api/recipes/download_shopping_cart/ - Список покупок в PDF
    """
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [IsAuthorOrReadOnly, ]

    def get_queryset(self):

        queryset = Recipe.objects.all()
        user = self.request.user

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited == '1':
            queryset = queryset.filter(is_favorited=user)

        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_in_shopping_cart == '1':
            queryset = queryset.filter(is_in_shopping_cart=user)

        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return RecipePostSerializer
        return RecipeGetSerializer

    @action(methods=['get'], detail=False, url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        user = self.request.user
        recipe_is_in_shopping_cart = Recipe.objects.filter(is_in_shopping_cart=user)
        shopping_cart = (IngredientForRecipe.objects
                         .filter(recipe__in=recipe_is_in_shopping_cart)
                         .values('ingredient__id')
                         .annotate(total=Sum('amount'))
                         .values('ingredient__name', 'total', 'ingredient__measurement_unit', )
                         .order_by('-total')
                         )

        buf = io.BytesIO()
        canv = canvas.Canvas(buf, pagesize=A4, bottomup=0)

        reportlab.rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/fonts')
        pdfmetrics.registerFont(TTFont('Courier New', 'cour.ttf', 'UTF-8'))

        canv.setFont('Courier New', 25)
        text_obj = canv.beginText()
        text_obj.setTextOrigin(200, 100)
        text_obj.textLine("Список покупок:")
        canv.drawText(text_obj)

        canv.setFont('Courier New', 14)
        text_obj = canv.beginText()
        text_obj.setTextOrigin(80, 150)
        nn = 0
        for line in shopping_cart:
            nn += 1
            stroka = f'{str(nn):>2}.' \
                     f'  {str(line.get("ingredient__name")):<25}   -   ' \
                     f'{str(line.get("total")):>8} {str(line.get("ingredient__measurement_unit")):<10}'
            text_obj.textLine(stroka)

        canv.drawText(text_obj)
        canv.showPage()
        canv.save()
        buf.seek(0)

        return FileResponse(buf, as_attachment=True, filename='shopping_cart.pdf')


class SubscribetViewSet(mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """
    POST   /users/{id}/subscribe/ - Подписаться на пользователя
    DEL    /users/{id}/subscribe/ - Отписаться от пользователя
    """
    serializer_class = SubscribetSerializer
    queryset = Subscription.objects.all()
    pagination_class = None
    permission_classes = [IsAuthorOrAuthReadOnly, ]

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
    serializer_class = SubscriptionsSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthorOrAuthReadOnly, ]

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
    serializer_class = RecipeMiniSerializer
    queryset = Recipe.objects.all()
    pagination_class = None
    permission_classes = [IsAuthorOrAuthReadOnly, ]

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

    serializer_class = RecipeMiniSerializer
    queryset = Recipe.objects.all()
    pagination_class = None
    permission_classes = [IsAuthorOrAuthReadOnly, ]

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
