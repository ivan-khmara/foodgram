from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название',

    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цветовой HEX-код',

    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Slug',

    )

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='•	Название',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения',
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'


class IngredientForRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Название',
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(1), ],
        verbose_name='Количество',
    )

    def __str__(self):
        return f'{self.ingredient.name} - {self.amount}'

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингридиент для рецепта'
        verbose_name_plural = 'Ингридиенты для рецептов'


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='Recipes',
        verbose_name='Автор публикации',
    )
    ingredients = models.ManyToManyField(
        IngredientForRecipe,
        verbose_name='Ингредиенты',
    )

    is_favorited = models.ManyToManyField(
        User,
        related_name='is_favoriteds',
        verbose_name='В избранном'
    )
    is_in_shopping_cart = models.ManyToManyField(
        User,
        related_name='is_in_shopping_carts',
        verbose_name='В списке покупок'
    )

    name = models.TextField(
        max_length=200,
        verbose_name='Название'
    )
    image = models.ImageField(
        verbose_name='Картинка'
    )

    text = models.TextField(
        verbose_name='Текстовое описание'
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1), ],
        verbose_name='Время приготовления в минутах'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-created',)
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

    class Meta:
        ordering = ('pk',)
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
