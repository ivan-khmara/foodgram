from django.forms import model_to_dict
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from .models import User, Tag, Ingredient, Recipe, Subscription, IngredientForRecipe
from .validators import validate_user
from drf_writable_nested import WritableNestedModelSerializer



class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(default=False)

    class Meta:
        model = User
        order_by = (('username',))
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed'
                  )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        try:
            Subscription.objects.get(user=user, author=obj)
            return True
        except:
            return False


class UserCreateSerializerC(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  "password",
                  )


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

class IngredientForRecipeSerializerPost(serializers.ModelSerializer):

    id = serializers.SlugRelatedField(
        slug_field = 'id',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientForRecipe
        fields = ("id",
                  "amount",
                  )

    def create(self, validated_data):
        print('я сюда не попадаю')
        print(validated_data)




class IngredientForRecipeSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientForRecipe
        fields = (
            "id",
            'name',
            "measurement_unit",
            'amount',
        )

    def get_id(self, obj):
        return obj.ingredient.pk

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientForRecipeSerializer(many=True)
    image = Base64ImageField(required=False)
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
                  'image',
                  'text',
                  'cooking_time',
                  )


    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user in obj.is_favorited.all():
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user in obj.is_in_shopping_cart.all():
            return True
        return False


class RecipeSerializerPost(serializers.ModelSerializer):

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )

    author = UserSerializer(read_only=True)
    ingredients = IngredientForRecipeSerializerPost(many=True,
                                                    write_only = True
                                                    )
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'name',
                  'image',
                  'text',
                  'cooking_time',
                  )
        #depth = 2

        def get_is_favorited(self, obj):
            user = self.context['request'].user
            if user in obj.is_favorited.all():
                return True
            return False

        def get_is_in_shopping_cart(self, obj):
            user = self.context['request'].user
            if user in obj.is_in_shopping_cart.all():
                return True
            return False

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     print(representation)
    #
    #     return representation

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = get_object_or_404(User, pk=1)
        recipe = Recipe.objects.create(**validated_data, author=author)
        recipe.tags.set(tags)
        for ing in ingredients:
            ingredient = ing.get('id')
            amount = ing.get('amount')
            tmp = IngredientForRecipe.objects.create(ingredient=ingredient, amount= amount)
            recipe.ingredients.add(tmp)
        return recipe

    # def update(self, instance, validated_data):
    #     return

    # def get_image(self):
    #     image = base64.b64decode(str(base64String))
    #     fileName = 'test.jpeg'
    #
    #     imagePath = FILE_UPLOAD_DIR + fileName
    #
    #     img = Image.open(io.BytesIO(image))
    #     img.save(imagePath, 'jpeg')
    #     return fileName


# class DownloadShoppingSerializer(serializers.ModelSerializer):


class SubscriptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'


class SubscribetSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ('author',
                  )
        read_only_fields = ('user', 'author')


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time"
        )


class FavoriteSerializer(ShoppingCartSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time"
        )
