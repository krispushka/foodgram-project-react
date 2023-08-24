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
            f'{ingredient["ringredient__name"]}'
            f'({ingredient["ingredient__measurement_unit"]}) - '
            f'{ingredient["amount"]}'
        )
    shopping_list_str = "\n".join(shopping_list)
    return shopping_list_str
