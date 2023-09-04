from recipes.models import IngredientRecipe
from django.db.models import Sum


def get_shopping_list(user):
    ingredients = (
        IngredientRecipe.objects
        .filter(recipe__shopping_list__user=user)
        .values(
            "ingredient__name",
            "ingredient__measurement_unit",
        )
        .annotate(amount=Sum("amount"))
    )

    shopping_list = []

    for ingredient in ingredients:
        shopping_list.append(
            f'{ingredient["ingredient__name"]}'
            f'({ingredient["ingredient__measurement_unit"]}) - '
            f'{ingredient["amount"]}\n'
        )
    return shopping_list
