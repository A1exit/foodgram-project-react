from django.contrib.auth import authenticate, get_user_model
from djoser.compat import get_user_email, get_user_email_field_name
from djoser.conf import settings
from djoser.serializers import UserCreateSerializer
from recipes.models import Recipe
from rest_framework import serializers

from .models import Follow

User = get_user_model()


class TokenCreateSerializer(serializers.Serializer):
    password = serializers.CharField(required=False,
                                     style={'input_type': 'password'})

    default_error_messages = {
        'invalid_credentials':
            settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR,
        'inactive_account':
            settings.CONSTANTS.messages.INACTIVE_ACCOUNT_ERROR,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

        self.email_field = get_user_email_field_name(User)
        self.fields[self.email_field] = serializers.EmailField()

    def validate(self, attrs):
        password = attrs.get('password')
        email = attrs.get('email')
        self.user = authenticate(
            request=self.context.get('request'), email=email, password=password
        )
        if not self.user:
            self.user = User.objects.filter(email=email).first()
            if self.user and not self.user.check_password(password):
                self.fail('invalid_credentials')
        if self.user and self.user.is_active:
            return attrs


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password')


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, author):
        user = self.context['request'].user
        if (user.is_authenticated and Follow.objects.filter(
                user=user,
                author=author).exists()):
            return True
        return False

    def update(self, instance, validated_data):
        email_field = get_user_email_field_name(User)
        if settings.SEND_ACTIVATION_EMAIL and email_field in validated_data:
            instance_email = get_user_email(instance)
            if instance_email != validated_data[email_field]:
                instance.is_active = False
                instance.save(update_fields=['is_active'])
        return super().update(instance, validated_data)


class FollowingRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count',)

    def get_recipes(self, author):
        recipes = author.recipes.all()
        return FollowingRecipeSerializer(recipes, many=True).data

    def get_is_subscribed(self, author):
        if Follow.objects.filter(author=author,
                                 user=self.context['request'].user).exists():
            return True
        return False

    def get_recipes_count(self, author):
        return author.recipes.count()
