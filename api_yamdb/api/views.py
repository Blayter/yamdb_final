from rest_framework import status, viewsets, filters, mixins
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from reviews.models import User, Title, Category, Genre, Review
from .filters import TitleFilter
from api.get_unique_code_and_token import (
    create_confirmation_code,
    send_code_to_mail_of_user,
    get_tokens_for_user
)
from .serializers import (
    UserSerializer,
    ReadTitleSerializer,
    WriteTitleSerializer,
    CategorySerializer,
    ReviewSerializer,
    CommentSerializer,
    GenreSerializer,
    AuthSerializer,
    UserRoleSerializer,
    TokenSerializer
)
from .permissions import (
    AuthorOrModeratorOrAdminOrReadonly,
    AdminOrReadonly,
    SelfOrAdmin
)


class ListCreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    pass


class CategoryViewSet(ListCreateDestroyViewSet):
    permission_classes = (AdminOrReadonly,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenresViewSet(ListCreateDestroyViewSet):
    permission_classes = (AdminOrReadonly,)
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminOrReadonly,)
    queryset = Title.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return WriteTitleSerializer
        if self.action == 'partial_update':
            return WriteTitleSerializer
        return ReadTitleSerializer

    pagination_class = LimitOffsetPagination
    filterset_class = TitleFilter
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year', 'category__slug', 'genre__slug')


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = (AuthorOrModeratorOrAdminOrReadonly,)
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        reviews = title.reviews.all()
        return reviews

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (AuthorOrModeratorOrAdminOrReadonly,)
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        queryset = review.comments.all()
        return queryset

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (SelfOrAdmin,)
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    queryset = User.objects.all()
    lookup_field = 'username'

    @action(detail=False, methods=['get', 'patch'], url_path='me',
            permission_classes=(IsAuthenticated,),
            serializer_class=UserRoleSerializer)
    def get_patch_me_url(self, request):
        if request.method != 'GET':
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class SendMessageForConfirmationCode(APIView):
    def post(self, request):
        username = request.data.get('username')
        mail = request.data.get('email')
        if username == 'me':
            return Response(
                {"message": "'me' не может быть username"},
                status.HTTP_400_BAD_REQUEST
            )
        user = User.objects.filter(email=mail)
        if len(user) > 0:
            if user[0].username != username:
                return Response(
                    {"message": "Пользователь с таким"
                     " 'email' уже зарегистрирован!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            confirmation_code = user[0].confirmation_code
        else:
            confirmation_code = create_confirmation_code()
            data = {'email': mail, 'confirmation_code': confirmation_code,
                    'username': username}
            serializer = AuthSerializer(data=data)
            if not serializer.is_valid(raise_exception=True):
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        send_code_to_mail_of_user(mail, confirmation_code, username)
        return Response({'email': mail, 'username': username})


class SendMessageForToken(APIView):
    def post(self, request):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')
        serializer = TokenSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        user = get_object_or_404(User, username=username)
        if user.confirmation_code != confirmation_code:
            return Response(
                {'message': 'Уникальный код не действителен!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        response = {'token': get_tokens_for_user(user)}
        return Response(response, status=status.HTTP_200_OK)
