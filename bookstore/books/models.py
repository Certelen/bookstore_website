from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.dispatch import receiver
from django.db.models.signals import pre_delete, m2m_changed

import books.validator as val

event_choise = [('books', 'Книги'), ('genres', 'Жанры'),
                ('all_books', 'Все')]


class Event(models.Model):
    event_on = models.CharField(
        'Цель акции',
        max_length=200,
        choices=event_choise
    )
    genres = models.ManyToManyField(
        'Genre',
        related_name='event',
        verbose_name='Акция на жанры',
        blank=True
    )
    books = models.ManyToManyField(
        'Book',
        related_name='event',
        verbose_name='Акция на книги',
        blank=True
    )
    all_books = models.BooleanField(
        'На все книги',
        default=False
    )
    discount = models.PositiveIntegerField(
        'Скидка в процентах',
        default=0,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(0)
        ]
    )

    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'

    def __str__(self):
        return f'Скидка {self.discount} на {self.get_event_on_display()}'


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
    discount = models.IntegerField(
        'Текущая скидка в процентах',
        default=0,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(0)
        ]
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

    def get_price(self):
        return int(self.price * ((100 - self.discount)/100))

    @receiver(pre_delete, sender=Event)
    def delete_event(sender, instance, **kwargs):
        books = instance.books.all()
        for book in books:
            book_events = book.event.all().exclude(id=instance.id)
            new_discount = 0
            for event in book_events:
                if instance.discount < event.discount:
                    new_discount = book.discount
                    break
                if new_discount < event.discount:
                    new_discount = event.discount
            book.event.remove(instance)
            book.discount = new_discount
            book.save()


class Banner(models.Model):
    image = models.ImageField(
        'Изображение банера',
        upload_to='banners/',
        help_text='Желательно 1200x300\
             из которых 600px в середине - зона с информацией'
    )
    close = models.BooleanField(
        'Не показывать на сайте',
        default=False
    )

    class Meta:
        verbose_name = 'Баннер'
        verbose_name_plural = 'Баннеры'

    def __str__(self):
        return 'Не показывается' if self.close else 'Показывается'


def book_event_change(instance, action, pk_set, **kwargs):
    if action == "post_add":
        copy_pk_set = pk_set.copy()
        while copy_pk_set:
            book = Book.objects.get(id=copy_pk_set.pop())
            if book.discount < instance.discount:
                book.discount = instance.discount
            book.save()


m2m_changed.connect(book_event_change, sender=Event.books.through)
