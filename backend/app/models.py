from django.contrib.auth.models import AbstractUser
from datetime import date
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True
    )
    color = models.CharField(
        max_length=7,
        unique=True
    )
    slug = models.SlugField(
        max_length=200,
        unique=True
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'


class IngredientForRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        MinValueValidator(0),
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='Recipes',
        verbose_name='Автор рецепта',
        help_text='Автор рецепта'
    )
    ingredients = models.ManyToManyField(IngredientForRecipe)  # не все так просто

    is_favorited = models.ManyToManyField(
        User,
        related_name='is_favoriteds'
        )
    is_in_shopping_cart = models.ManyToManyField(
        User,
        related_name='is_in_shopping_carts'
        )

    name = models.TextField(
        max_length=200,
    )
    image = models.ImageField()

    text = models.TextField()
    cooking_time = models.IntegerField(MinValueValidator(0))
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['name', 'year'],
        #         name='unique_name_year'
        #     )
        # ]
        ordering = ('id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )
