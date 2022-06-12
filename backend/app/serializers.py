from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import User, Tag, Ingredient, Recipe, Subscription, IngredientForRecipe


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


class IngredientForRecipePostSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        slug_field='id',
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


class IngredientForRecipeGetSerializer(serializers.ModelSerializer):
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
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time',
                  )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['is_favorited'] = bool(self.context['request'].user in instance.is_favorited.all())
        representation['is_in_shopping_cart'] = bool(self.context['request'].user in instance.is_in_shopping_cart.all())
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
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time',
                  )
        read_only_fields = ('is_favorited', 'is_in_shopping_cart',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(instance.tags, many=True).data
        representation['ingredients'] = IngredientForRecipeGetSerializer(instance.ingredients, many=True).data
        representation['is_favorited'] = bool(self.context['request'].user in instance.is_favorited.all())
        representation['is_in_shopping_cart'] = bool(self.context['request'].user in instance.is_in_shopping_cart.all())
        return representation

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data, author=author)

        recipe.tags.set(tags)

        for ing in ingredients:
            ingredient = ing.get('id')
            amount = ing.get('amount')
            tmp = IngredientForRecipe.objects.create(ingredient=ingredient, amount=amount)
            recipe.ingredients.add(tmp)

        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)

        tags = validated_data.get('tags', False)
        if tags:
            instance.tags.clear()
            instance.tags.set(tags)

        ingredients = validated_data.get('ingredients', False)
        if ingredients:
            tmp = instance.ingredients.all()
            tmp.delete()
            for ing in ingredients:
                ingredient = ing.get('id')
                amount = ing.get('amount')
                tmp = IngredientForRecipe.objects.create(ingredient=ingredient, amount=amount)
                instance.ingredients.add(tmp)

        instance.save()
        return instance


class RecipeMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time"
        )


# class DownloadShoppingSerializer(serializers.ModelSerializer):


class SubscriptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        query_params = self.context['request'].query_params.get('recipes_limit', False)
        queryset = instance.Recipes.all()
        if query_params:
            queryset = instance.Recipes.all()[:int(query_params)]
        user = self.context['request'].user  # текущий пользователь
        follower = [i.author for i in user.follower.all()]  # список на кого подписан
        representation['is_subscribed'] = bool(instance in follower)
        representation['recipes'] = RecipeMiniSerializer(queryset, many=True).data
        representation['recipes_count'] = instance.Recipes.count()
        return representation


class SubscribetSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ('author',
                  )
        read_only_fields = ('user', 'author')
