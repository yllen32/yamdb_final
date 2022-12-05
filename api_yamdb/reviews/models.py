from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Админ'),
    ]
    bio = models.TextField(verbose_name='Biography', blank=True)
    role = models.CharField(
        max_length=9, verbose_name='Role', choices=ROLE_CHOICES, default=USER
    )
    password = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN


class Categorie(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.TextField()
    category = models.ForeignKey(
        Categorie, on_delete=models.SET_NULL,
        related_name='titles', blank=False, null=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        blank=True,
    )
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)
    score = models.IntegerField(
        'Оценка',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        help_text='Введдите оценку',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique review')
        ]

    def __str__(self):
        return self.text[:30]


class Comment(models.Model):
    """Комментарии пользователя на отзыв."""
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментируемый отзыв'
    )
    text = models.TextField(
        max_length=5000,
        verbose_name='Текст комментария')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания комментария'
    )

    def __str__(self):
        return f'{self.author.username}, {self.text}, {self.pub_date}'
