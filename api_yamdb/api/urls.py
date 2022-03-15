from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    GenresViewSet,
    CategoryViewSet,
    TitleViewSet,
    ReviewViewSet,
    CommentViewSet,
    SendMessageForConfirmationCode,
    SendMessageForToken
)


v1_router = DefaultRouter()
v1_router.register('users', UserViewSet, basename='user')
v1_router.register('titles', TitleViewSet)
v1_router.register('categories', CategoryViewSet)
v1_router.register('genres', GenresViewSet)
v1_router.register(
    r'titles/(?P<title_id>[\d+]+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>[\d+]+)/reviews/(?P<review_id>[\d+]+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/auth/token/', SendMessageForToken.as_view()),
    path('v1/auth/signup/', SendMessageForConfirmationCode.as_view()),
    path('v1/', include(v1_router.urls)),
]
