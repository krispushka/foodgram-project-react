from api.serializers import (RecipeCreateSerializer,
                             RecipeReadSerializer,
                             ShortRecipeInfoSerializer,
                             TagSerializer
                             )
from django.shortcuts import get_object_or_404
from recipes.models import (Favorite,
                            Ingredient,
                            Recipe,
                            ShoppingCard,
                            Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated)
from rest_framework.response import Response
from django.db.models import Sum
from django.http import HttpResponse


# class UserViewSet(UserViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

#     def get_serializer_class(self):
#         if self.request.method == 'POST':
#             return UserCreateSerializer
#         return UserSerializer

#     def perform_create(self, serializer):
#         serializer.save(password=self.request.data['password'])


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return RecipeCreateSerializer
        return RecipeReadSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = ShortRecipeInfoSerializer(recipe)
        if request.method == 'POST':
            Favorite.objects.get_or_create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            Favorite.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = ShortRecipeInfoSerializer(recipe)
        if request.method == 'POST':
            ShoppingCard.objects.get_or_create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            ShoppingCard.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            ShoppingCard.objects
            .filter(user=user)
            .values('recipe__recipes_ingredient__ingredient__name',
                    'recipe__recipes_ingredient__ingredient__measurement_unit')
            .annotate(amount=Sum('recipe__recipes_ingredient__amount')))

        shopping_list = []

        for ingredient in ingredients:
            shopping_list.append(
                f'{ingredient["recipe__recipes_ingredient__ingredient__name"]}'
                f'({ingredient["recipe__recipes_ingredient__ingredient__measurement_unit"]}) - '
                f'{ingredient["amount"]}'
            )
        shopping_list_str = '\n'.join(shopping_list)
        return HttpResponse(
            shopping_list_str,
            {
                "Content-Type": "text/plain",
                "Content-Disposition": "attachment; filename='shopping_list.txt'",
            },
        )
