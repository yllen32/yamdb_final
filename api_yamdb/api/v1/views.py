from rest_framework import viewsets, status, permissions, filters
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view, permission_classes, action, throttle_classes)
from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, DestroyModelMixin)
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg

from .permissions import (
    IsSuperUserOrAdminPermission, AdminOrReadOnly, IsAuthorOrReadOnly)
from reviews.models import (
    User, Genre, Categorie, Title, Review)
from .serializers import (
    AuthSerializer, TokenSerializer, UserSerializer,
    GenresSerializer, CategoriesSerializer, TitleReadSerializer,
    TitlesPOSTSerializer, CommentSerializer, ReviewSerializer, MeSerializer)
from .throttles import NoGuessRateThrottle
from .utils import (
    get_tokens_for_user, send_confirmation_mail, get_confirmation_code)
from .filters import TitleFilter


class CreateDeleteViewSet(CreateModelMixin, ListModelMixin,
                          DestroyModelMixin, viewsets.GenericViewSet):
    pass


class GenresViewSet(CreateDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenresSerializer
    permission_classes = (AdminOrReadOnly, )
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoriesViewSet(CreateDeleteViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (AdminOrReadOnly, )
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)
    lookup_field = 'slug'


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (AdminOrReadOnly, )
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return TitlesPOSTSerializer
        return TitleReadSerializer

    def get_queryset(self):
        return Title.objects.all().annotate(rating=Avg('reviews__score'))


class ReviewViewSet(viewsets.ModelViewSet):
    """Обработчик запросов к модели Review."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        return get_object_or_404(
            Title, pk=self.kwargs.get('title_id')
        ).reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Обработчик запросов к модели Comment."""
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        return get_object_or_404(
            Review, pk=self.kwargs.get('review_id')
        ).comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, review_id=review.id)


@api_view(['POST'])
def signup(request):
    """
    Sends confirmation mail to mentioned email, and save data about user.

    In case if user already exists, it send new email with confirmation code.
    """
    serializer = AuthSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    username = serializer.validated_data['username']
    user = User.objects.filter(username=username, email=email)
    if not user.exists():
        user = User.objects.create_user(email=email, username=username)
    confirmation_code = get_confirmation_code(user=user)
    send_confirmation_mail(email=email, code=confirmation_code)
    return Response(data=request.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([NoGuessRateThrottle])
def token(request):
    """Get and send a token to user which has been validated."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    confirmation_code = serializer.validated_data['confirmation_code']
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username'],
    )
    if not default_token_generator.check_token(user, confirmation_code):
        return Response(
            'Confirmation code is not valid',
            status=status.HTTP_400_BAD_REQUEST
        )
    token = get_tokens_for_user(user=user)
    return Response(data=token, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSuperUserOrAdminPermission,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    search_fields = ('username',)

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request,):
        """
        Get or update (patch method) inf about requested user.
        """
        me = get_object_or_404(User, username=request.user.username)
        if request.method == 'GET':
            serializer = MeSerializer(me)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = MeSerializer(me, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
