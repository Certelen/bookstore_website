from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

import books.validator as val


class Genre(models.Model):
    name = models.CharField(
        'Название книги',
        help_text='Название книги',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class BookFiles(models.Model):
    book = models.ForeignKey(
        'Book',
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='Книга',
    )
    name = models.CharField(
        'Формат файла',
        max_length=8,
        choices=[
            ('PDF', 'PDF'),
            ('FB2', 'FB2'),
            ('IOS.EPUB', 'IOS.EPUB'),
            ('EPUB', 'EPUB'),
            ('MOBI', 'MOBI')
        ]
    )
    file = models.FileField(
        unique=True,
        upload_to=val.book_directory_path,
        validators=[val.validate_file]
    )

    class Meta:
        verbose_name = 'Файлы книги'
        verbose_name_plural = 'Файлы книг'
        unique_together = [["book", "name"]]


class Book(models.Model):
    name = models.CharField(
        'Название книги',
        help_text='Название книги',
        max_length=200,
    )
    author = models.CharField(
        'Автор книги',
        help_text='Автор книги',
        max_length=200,
    )
    description = models.TextField(
        'Описание книги'
    )
    fragment = models.TextField(
        'Ознакомительный отрывок книги'
    )
    pages = models.PositiveIntegerField(
        'Количество страниц'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='books',
        verbose_name='Жанры книги',
    )
    main_image = models.ImageField(
        'Главное изображение книги',
        upload_to='books/',
        help_text='Изображение книги в превью',
    )
    buying = models.PositiveIntegerField(
        'Количество покупок',
        default=0
    )
    price = models.PositiveIntegerField(
        'Цена книги',
        help_text='Цена товара',
        default=0
    )
    score = models.PositiveIntegerField(
        'Оценка книги',
        help_text='Оценка товара',
        default=0,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(0)
        ]
    )
    release = models.DateField(
        'Дата выпуска книги'
    )
    created = models.DateField(
        'Дата добавления книги на сайт',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ('-created', )
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'

    def __str__(self):
        return self.name


class BookImage(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Книга',
    )
    image = models.ImageField(
        'Изображения книги',
        upload_to='books/',
        help_text='Загрузка картинки'
    )

    class Meta:
        verbose_name = 'Изображения книги'
        verbose_name_plural = 'Изображения книг'


class Banner(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='banner',
        verbose_name='Связан с книгой',
        blank=True,
        null=True
    )
    image = models.ImageField(
        'Изображение банера',
        upload_to='banners/',
        help_text='Загрузка картинки баннера'
    )
    close = models.BooleanField(
        'Не показывать на сайте',
        default=False
    )

    class Meta:
        verbose_name = 'Баннер'
        verbose_name_plural = 'Баннеры'
