import io

from django.db.models import F, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import RecipeFilter
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)
from .permissions import AuthorOrReadOnly
from .serializers import (CreateRecipeSerializer, FavoriteSerializer,
                          IngredientsSerializer, TagSerializer,
                          ViewRecipeSerializer)
from .utils import get_shopping_list


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
    pagination_class = None


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    http_method_names = ['get']
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = ViewRecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = RecipeFilter
    ordering_fields = ('id',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ViewRecipeSerializer
        return CreateRecipeSerializer


class APIFavorite(APIView):

    def delete(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        subscription = get_object_or_404(Favorite, user=user,
                                         recipe=recipe)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        Favorite.objects.get_or_create(user=user, recipe=recipe)
        serializer = FavoriteSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class APIShoppingCart(APIView):

    def get(self, request):
        return get_shopping_list(self, request)

    def delete(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        subscription = get_object_or_404(ShoppingCart, user=user,
                                         recipe=recipe)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
        serializer = FavoriteSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
