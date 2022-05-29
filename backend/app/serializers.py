from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from .models import User, Tag, Ingredient, Recipe, Follow, IngredientForRecipe
from .validators import validate_user


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(default=False)

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed'
                  )

    def get_is_subscribed(self, obj):
        return False


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id",
                  "name",
                  "color",
                  "slug",
                  )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id",
                  "name",
                  "measurement_unit",
                  )


class RecipeSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientSerializer(many=True)

    is_favorited = serializers.SerializerMethodField(default=False)
    is_in_shopping_cart = serializers.SerializerMethodField(default=False)

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
#                  'image',
                  'text',
                  'cooking_time',
                  )

    def get_is_favorited(self, obj):
        return False

    def is_in_shopping_cart(self, obj):
        return False


# class DownloadShoppingSerializer(serializers.ModelSerializer):
#
#
#
# class ShoppingCarSerializer(serializers.ModelSerializer):
#
#
#
# class FavoriteSerializer(serializers.ModelSerializer):
#
#
#
#
# class SubscriptionsSerializer(serializers.ModelSerializer):
#
#
#
#
# class SubscribetSerializer(serializers.ModelSerializer):




class UserForAdminSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'email', 'role')


class GetConfirmationCodeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150, validators=[validate_user])
    email = serializers.EmailField(max_length=254,)

    class Meta:
        model = User
        fields = ['username', 'email']

    def create(self, validated_data):
        user, created = User.objects.get_or_create(**validated_data)
        return user


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()
