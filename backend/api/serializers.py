from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import (Ingredient, IngredientForRecipe, Recipe, Subscription,
                     Tag, User)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(default=False)

    class Meta:
        model = User
        order_by = ('username',)
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed'
                  )

    def get_is_subscribed(self, obj):

        user = self.context['request'].user
        return bool(
            user.is_authenticated
            and Subscription.objects.filter(user=user, author=obj).exists()
        )


class UserCreateSerializerC(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password',
                  )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id',
                  'name',
                  'color',
                  'slug',
                  )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id',
                  'name',
                  'measurement_unit',
                  )


class IngredientForRecipePostSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientForRecipe
        fields = ('id',
                  'amount',
                  )


class IngredientForRecipeGetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.pk')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientForRecipe
        fields = ('id',
                  'name',
                  'measurement_unit',
                  'amount',
                  )


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientForRecipeGetSerializer(many=True)
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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['is_favorited'] = bool(
            self.context['request'].user in instance.fans.all()
        )
        representation['is_in_shopping_cart'] = bool(
            self.context['request'].user in instance.shoppers.all()
        )
        return representation


class RecipePostSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    author = UserSerializer(read_only=True)
    ingredients = IngredientForRecipePostSerializer(many=True,
                                                    write_only=True
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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(instance.tags, many=True).data
        representation['ingredients'] = IngredientForRecipeGetSerializer(
            instance.ingredients, many=True
        ).data
        representation['is_favorited'] = bool(
            self.context['request'].user in instance.fans.all()
        )
        representation['is_in_shopping_cart'] = bool(
            self.context['request'].user in instance.shoppers.all()
        )
        return representation

    @staticmethod
    def update_tags(instance, tags):
        if tags:
            instance.tags.clear()
            instance.tags.set(tags)
        return instance

    @staticmethod
    def create_or_update_ingredients(instance, ingredients):
        if ingredients:
            ingredients_old = instance.ingredients.all()
            ingredients_old.delete()
            objs = [
                IngredientForRecipe(
                    ingredient=ingr.get('id'),
                    amount=ingr.get('amount')
                )
                for ingr in ingredients
            ]
            ingr_for_recipe = IngredientForRecipe.objects.bulk_create(objs)
            instance.ingredients.set(ingr_for_recipe)
        return instance

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data, author=author)
        recipe.tags.set(tags)
        self.create_or_update_ingredients(
            recipe,
            ingredients
        )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        self.update_tags(instance, validated_data.get('tags', False))
        self.create_or_update_ingredients(
            instance,
            validated_data.get('ingredients', False)
        )
        instance.save()
        return instance


class RecipeMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionsSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField(default=False)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return bool(
            user.is_authenticated
            and Subscription.objects.filter(user=user, author=obj).exists()
        )

    def get_recipes(self, obj):
        query_params = self.context['request'].query_params.get(
            'recipes_limit',
            False
        )
        queryset = obj.recipes.all()
        if query_params:
            queryset = obj.recipes.all()[:int(query_params)]
        return RecipeMiniSerializer(queryset, many=True).data


class SubscribetSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Subscription
        fields = ('author', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('author', 'user'),
                message='Вы уже были подписаны на автора'
            )
        ]

    def validate(self, data):
        if data['author'] == data['user']:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя')
        return data
