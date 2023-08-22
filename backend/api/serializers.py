from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCard, Tag)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import Follow, User


class UserSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, following=obj).exists()


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = (
            "id",
            "amount",
        )


class ShortRecipeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True, read_only=True, source="ingredientrecipe_set"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        return ShoppingCard.objects.filter(
            user=request.user,
            recipe=obj).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
    )
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            "author",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )

    def add_ingredients(self, recipe, ingredients):
        for ingredient in ingredients:
            ingredient, status = IngredientRecipe.objects.get_or_create(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, id=ingredient["id"]),
                amount=ingredient["amount"],
            )

    def create(self, validated_data):
        request = self.context.get("request")
        author = request.user
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        IngredientRecipe.objects.filter(recipe=recipe).delete()
        self.add_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe


class UserSubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = ShortRecipeInfoSerializer(many=True)
    recipes_count = serializers.ReadOnlyField(source="following.recipes.count")

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "recipes_count",
            "is_subscribed",
            "recipes",
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=("user", "following"),
                message="Вы уже подписаны на этого автора",
            )
        ]

    def validate(self, data):
        request = self.context.get("request")
        following = self.instance
        if request.user == following:
            raise ValidationError("Вы не можете подписаться на самого себя.")
        return data

    def get_is_subscribed(self, data):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user,
            following=data
        ).exists()

    def get_recipes_count(self, data):
        return Recipe.objects.filter(author=data.id).count()
