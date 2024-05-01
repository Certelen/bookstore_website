from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import MaxValueValidator, MinValueValidator

from books.models import Book, Genre


class ViewedGenres(models.Model):
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='viewed',
        verbose_name='Пользователь',
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='viewed',
        verbose_name='Жанр книги',
    )

    class Meta:
        verbose_name = 'Просмотренный пользователем жанр'
        verbose_name_plural = 'Просмотренные пользователями жанры'

    def __str__(self):
        return self.user.username + ' посмотрел ' + self.genre.name


class CustomUser(AbstractUser):
    email = models.EmailField(
        _("email address"),
        unique=True,
        help_text=_(
            "150 characters or fewer."
        ),
        error_messages={
            "unique": _("Пользователь с такой почтой уже существует."),
        },
    )
    favorite_books = models.ManyToManyField(
        Book,
        related_name='users_favorite',
        verbose_name='Избранные книги',
        blank=True,
    )
    buyed_books = models.ManyToManyField(
        Book,
        related_name='users_buying',
        verbose_name='Купленные книги',
        blank=True,
    )
    most_viewed_genres = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='users_viewed',
        verbose_name='Наиболее просматриваемый жанр',
        blank=True,
        null=True
    )
    viewed_genres = models.IntegerField(
        'Количество просмотренных жанров',
        default=0,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @receiver(post_save, sender=ViewedGenres)
    def user_view_book_page(sender, instance, created, **kwargs):
        if created:
            user = instance.user
            user.most_viewed_genres = Genre.objects.get(
                id=ViewedGenres.objects.values('genre')
                .annotate(viewed=models.Count('genre'))
                .order_by('-viewed')[0]['genre']
            )
            user.viewed_genres += 1
            if user.viewed_genres >= 20:
                iteration = 0
                while user.viewed_genres != 20:
                    print(iteration)
                    user.viewed_genres -= 1
                    early_genre = ViewedGenres.objects.filter(
                        user=user)[iteration]
                    print(early_genre)
                    early_genre.delete()
                    iteration += 1
            user.save()


class Review(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Пользователь оставивший отзыв',
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Книга на которую оставляется отзыв',
    )
    comment = models.TextField(
        'Текст отзыва',
        help_text='Текст отзыва',
    )
    score = models.PositiveSmallIntegerField(
        'Оценка книги',
        help_text='Оценка книги',
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ]
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.user} оставил отзыв к {self.book}'


class Order(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='order',
        verbose_name='Заказ пользователя',
    )
    buying = models.BooleanField(
        'Факт совершения покупки',
        help_text='Факт совершения покупки',
        default=False,
    )
    book = models.ManyToManyField(
        Book,
        related_name='order',
        verbose_name='Книги',
        blank=True
    )
    payment = models.CharField(
        'id платежа',
        max_length=200,
        blank=True,
        null=True
    )
    close = models.BooleanField(
        'Возможность изменять заказ',
        help_text='Возможность изменять заказ',
        default=False,
    )
    close_data = models.DateField(
        "Дата покупки",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ {self.user}, {"Закрыт" if self.close else "Не закрыт"}'

    @receiver(post_save, sender=CustomUser)
    def create_first_user_order(sender, instance, created, **kwargs):
        if created:
            Order.objects.create(user=instance)
