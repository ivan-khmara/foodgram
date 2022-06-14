from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint


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
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения',
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


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
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор публикации',
    )
    ingredients = models.ManyToManyField(
        IngredientForRecipe,
        verbose_name='Ингредиенты',
    )

    fans = models.ManyToManyField(
        User,
        verbose_name='В избранном',
        related_name='fans'
    )
    shoppers = models.ManyToManyField(
        User,
        verbose_name='В списке покупок',
        related_name='shoppers'
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
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            ),
        ]
