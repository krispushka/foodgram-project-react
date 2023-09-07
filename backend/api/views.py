from django.db.models import Exists, OuterRef
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe,
                            ShoppingCard, Tag)
from api.filters import RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (RecipeCreateSerializer, RecipeReadSerializer,
                             ShortRecipeInfoSerializer, TagSerializer,
                             UserSubscribeSerializer)
from api.services import get_shopping_list
from users.models import Follow, User


class GetObjectMixin:
    def func_to_add(self, request, pk, Model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = ShortRecipeInfoSerializer(recipe)
        Model.objects.get_or_create(user=user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def func_to_delete(self, request, pk, Model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        Model.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPagination
    permission_classes = (AllowAny,)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        page = self.paginate_queryset(queryset)
        serializer = UserSubscribeSerializer(
            page,
            many=True,
            context={"request": request},
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        following = get_object_or_404(User, id=id)
        user = request.user
        Follow.objects.get_or_create(user=user, following=following)
        serializer = UserSubscribeSerializer(
            following,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        following = get_object_or_404(User, id=id)
        user = request.user
        Follow.objects.filter(user=user, following=following).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)


class RecipeViewSet(GetObjectMixin, viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly, )
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Recipe.objects
            .select_related("author")
            .prefetch_related("tags")
        )
        if user.is_authenticated:
            favorite = Favorite.objects.filter(
                user=user, recipe=OuterRef("id"))
            is_in_shopping_cart = ShoppingCard.objects.filter(
                user=user, recipe=OuterRef("id")
            )
            queryset = queryset.annotate(
                is_favorited=Exists(favorite),
                is_in_shopping_cart=Exists(is_in_shopping_cart)
            )
        return queryset

    def get_serializer_class(self):
        if self.request.method in ("POST", "PUT", "PATCH", "DELETE"):
            return RecipeCreateSerializer
        return RecipeReadSerializer

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        return self.func_to_add(request, pk, Favorite)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk):
        return self.func_to_delete(request, pk, Favorite)

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return self.func_to_add(request, pk, ShoppingCard)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk):
        return self.func_to_delete(request, pk, ShoppingCard)

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        return FileResponse(
            get_shopping_list(user=user),
            as_attachment=True,
            filename="shop_list.txt"
        )
