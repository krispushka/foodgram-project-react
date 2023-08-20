from django.contrib import admin
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCard,
    Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "slug")


@admin.register(Ingredient)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ("author", "name", "text", "cooking_time")
    inlines = [IngredientRecipeInline]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )


@admin.register(ShoppingCard)
class ShoppingCardAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )
