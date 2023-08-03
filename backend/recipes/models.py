from django.db import models
from colorfield.fields import ColorField
from users.models import User
from django.core.validators import MinValueValidator


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Тег',
        unique=True,
        blank=True,)
    color = ColorField(
        format='hex',
        max_length=7,
        verbose_name='Цвет',
        blank=True,
        unique=True,
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Ingredients(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        blank=True,
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Еденица измерения',
        blank=True,
    )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'
    
    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        blank=True,
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        blank=True,
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка',
        blank=True,
    )
    text = models.TextField(
        verbose_name='Описание',
        blank=True,
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты',
        blank=True,
    )
    tag = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        blank=True,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                1,
                message='Время не может быть меньше 1 минуты'
            )
        ],
        blank=True,
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        blank=True,
    )

    def __str__(self):
        return (
            f'{self.recipe.name}, {self.ingredient.name}'
        )
    
    class Meta:
        verbose_name = 'ИнгредиентыРецепты'
        verbose_name_plural = 'ИнгредиентыРецепты'



class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    def __str__(self):
        return f'{self.user} - {self.recipe}'
    
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCard(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    def __str__(self):
        return f'{self.user} - {self.recipe}'

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
