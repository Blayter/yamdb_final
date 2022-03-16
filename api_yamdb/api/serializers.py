import datetime as dt

from django.db.models.aggregates import Avg
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.fields import CurrentUserDefault
from reviews.models import (
    Category,
    Comment,
    Genre,
    User,
    Review,
    Title,
)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('username', 'email', 'first_name', 'last_name',
                  'bio', 'role')
        model = User


class AuthSerializer(UserSerializer):

    class Meta:
        fields = ('username', 'email', 'role', 'confirmation_code')
        model = User


class UserRoleSerializer(UserSerializer):
    role = serializers.CharField(read_only=True)


class TokenSerializer(UserSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug',)
        model = Genre


class ReadTitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        rating = Review.objects.filter(
            title_id=obj.id
        ).aggregate(Avg('score'))
        return rating['score__avg']

    class Meta:
        fields = ('id', 'name', 'year', 'description',
                  'rating', 'category', 'genre')
        model = Title


class WriteTitleSerializer(ReadTitleSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True
    )

    def validate_year(self, value):
        year = dt.date.today().year
        if year < value:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего!'
            )
        return value


class TitleDafault:
    requires_context = True

    def __call__(self, serializer_field):
        view = serializer_field.context['view']
        title_id = view.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        default=CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )
    title = serializers.HiddenField(
        default=TitleDafault()
    )

    class Meta:
        fields = ('id', 'author', 'title', 'text', 'score', 'pub_date')
        model = Review

        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=['author', 'title'],
                message='Хватит! Ты уже оставил отзыв!'
            )
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        fields = ('id', 'author', 'text', 'pub_date')
        model = Comment
