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
        recipe = Recipe.objects.get(id=id)
        Favorite.objects.get_or_create(user=user, recipe=recipe)
        serializer = FavoriteSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class APIShoppingCart(APIView):

    def get(self, request):
        user = request.user
        shopping_list = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=user).values(
            name=F('ingredients__name'),
            unit=F('ingredients__measurement_unit')
        ).annotate(amount=Sum('amount')).order_by()
        font = 'DejaVuSerif'
        pdfmetrics.registerFont(
            TTFont('DejaVuSerif', 'DejaVuSerif.ttf', 'UTF-8'))
        buffer = io.BytesIO()
        pdf_file = canvas.Canvas(buffer)
        pdf_file.setFont(font, 24)
        pdf_file.drawString(
            150,
            800,
            'Список покупок.'
        )
        pdf_file.setFont(font, 14)
        from_bottom = 750
        for number, ingredient in enumerate(shopping_list, start=1):
            pdf_file.drawString(
                50,
                from_bottom,
                f'{number}.  {ingredient["name"]} - {ingredient["amount"]} '
                f'{ingredient["unit"]}'
            )
            from_bottom -= 20
            if from_bottom <= 50:
                from_bottom = 800
                pdf_file.showPage()
                pdf_file.setFont(font, 14)
        pdf_file.showPage()
        pdf_file.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True,
                            filename='shopping_list.pdf')

    def delete(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        subscription = get_object_or_404(ShoppingCart, user=user,
                                         recipe=recipe)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, id):
        user = request.user
        recipe = Recipe.objects.get(id=id)
        ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
        serializer = FavoriteSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
