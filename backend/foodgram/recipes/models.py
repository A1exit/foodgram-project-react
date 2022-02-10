from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        verbose_name='Цвет в HEX'
    )
    slug = models.SlugField(
        max_length=200,
        blank=True,
        unique=True,
        verbose_name='Уникальный слаг'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Единица измерения'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = "Ингредиенты"


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
        verbose_name='Список ингредиентов',
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='recipes'
    )
    image = models.ImageField(
        verbose_name="Картинка",
        upload_to="media/recipes/images/"
    )
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название'
    )
    text = models.TextField(
        blank=False,
        verbose_name='Описание'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1,
                                      message='Минимальное время'
                                              'приготовления - одна минута')],
        blank=False,
        verbose_name='Время приготовления (в минутах)'
    )

    def __str__(self):
        return self.name

    def favorites_count(self):
        return self.favorites.count()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        blank=False,
        on_delete=models.CASCADE,
        related_name='ingredient_to_recipe'
    )
    ingredients = models.ForeignKey(
        Ingredient,
        blank=False,
        on_delete=models.PROTECT,
        related_name='ingredient_to_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        blank=False,
        verbose_name='Количество ингредиентов',
        validators=(
            MinValueValidator(1, 'Минимальное количество ингредиентов 1'),
        )
    )

    def __str__(self):
        return f'{self.recipe.name} {self.ingredients.name}'

    class Meta:
        verbose_name = 'Рецепт и ингредиенты'
        verbose_name_plural = 'Рецепты и ингредиенты'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    def __str__(self):
        return f'{self.user}, {self.recipe}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='favorite')
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )

    def __str__(self):
        return f'{self.user}, {self.recipe}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='shopping_cart')
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
