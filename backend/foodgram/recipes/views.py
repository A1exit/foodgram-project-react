from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import IngredientSearchFilter, RecipeFilter
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .permissions import AuthorOrReadOnly
from .serializers import (CreateRecipeSerializer, FavoriteSerializer,
                          IngredientSerializer, TagSerializer,
                          ViewRecipeSerializer)
from .utils import get_shopping_list


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    http_method_names = ["get"]


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    http_method_names = ["get"]
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = ViewRecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = RecipeFilter
    filterset_fields = ("tags", "author")
    ordering_fields = ("id",)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ViewRecipeSerializer
        return CreateRecipeSerializer


def delete(request, id, model):
    user = request.user
    recipe = get_object_or_404(Recipe, id=id)
    obj = get_object_or_404(model, user=user, recipe=recipe)
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def post(request, id, model):
    user = request.user
    recipe = get_object_or_404(Recipe, id=id)
    model.objects.get_or_create(user=user, recipe=recipe)
    serializer = FavoriteSerializer(recipe, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class APIFavorite(APIView):

    def delete(self, request, id):
        return delete(request, id, Favorite)

    def post(self, request, id):
        return post(request, id, Favorite)


class APIShoppingCart(APIView):

    def get(self, request):
        return get_shopping_list(self, request)

    def delete(self, request, id):
        return delete(request, id, ShoppingCart)

    def post(self, request, id):
        return post(request, id, ShoppingCart)
