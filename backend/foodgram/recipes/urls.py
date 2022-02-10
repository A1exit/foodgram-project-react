from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (APIFavorite, APIShoppingCart, IngredientsViewSet,
                    RecipeViewSet, TagViewSet)

router = SimpleRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('recipes/download_shopping_cart/', APIShoppingCart.as_view()),
    path('', include(router.urls)),
    path('recipes/<int:id>/favorite/', APIFavorite.as_view()),
    path('recipes/<int:id>/shopping_cart/', APIShoppingCart.as_view()),
]
