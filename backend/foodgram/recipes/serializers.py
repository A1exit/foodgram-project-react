from rest_framework import serializers

from users.serializers import UserSerializer

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = '__all__'


class ViewRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientsSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, recipe):
        if (self.context['request'].user.is_authenticated
                and Favorite.objects.filter(
                    recipe=recipe,
                    user=self.context['request'].user).exists()
                and self.context['request'].user.is_authenticated):
            return True
        return False

    def get_is_in_shopping_cart(self, recipe):
        if (self.context['request'].user.is_authenticated
            and ShoppingCart.objects.filter(
                recipe=recipe,
                user=self.context['request'].user).exists()):
            return True
        return False


class TestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = '__all__'


class AddRecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_measurement_unit(self, ingredient):
        return ingredient.ingredients.measurement_unit

    def get_name(self, ingredient):
        return ingredient.ingredients.name


class CreateRecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = AddRecipeIngredientsSerializer(
        many=True,
        source='ingredient_to_recipe')
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'name',
                  'image',
                  'text',
                  'cooking_time',
                  'is_favorited',
                  'is_in_shopping_cart',)

    def create(self, validated_data):
        author = self.context['request'].user
        tags = self.context['request'].data['tags']
        ingredients = validated_data.pop('ingredient_to_recipe')
        recipe = Recipe.objects.create(**validated_data, author=author)
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            current_ingredient = ingredient['id']
            RecipeIngredient.objects.create(
                ingredients=current_ingredient, recipe=recipe,
                amount=ingredient["amount"]
            )
        return recipe

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def update(self, recipe, validated_data):
        if 'ingredients' in self.initial_data:
            ingredients = validated_data.pop('ingredient_to_recipe')
            recipe.ingredients.clear()
            for ingredient in ingredients:
                current_ingredient = ingredient['id']

                RecipeIngredient.objects.create(
                    ingredients=current_ingredient, recipe=recipe,
                    amount=ingredient["amount"]
                )
        if 'tags' in self.initial_data:
            tags_data = self.initial_data.pop('tags')
            recipe.tags.set(tags_data)
        return super().update(recipe, validated_data)

    def get_is_favorited(self, recipe):
        if Favorite.objects.filter(recipe=recipe,
                                   user=self.context['request'].user).exists():
            return True
        return False

    def get_is_in_shopping_cart(self, recipe):
        if ShoppingCart.objects.filter(
                recipe=recipe,
                user=self.context['request'].user).exists():
            return True
        return False


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')