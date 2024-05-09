from django.core.exceptions import ValidationError
import unidecode


def book_directory_path(instance, filename):
    """Создание пути для файлов"""
    return f'books_file/{instance.book.id}/{unidecode.unidecode(filename)}'


def book_image_directory_path(instance, filename):
    """Создание пути для изображений книг"""
    return f'books/{unidecode.unidecode(instance.book.name)}/'
    f'{unidecode.unidecode(filename)}'


def banner_image_directory_path(instance, filename):
    """Создание пути для изображений баннеров"""
    return f'banners/{unidecode.unidecode(filename)}'


def validate_file(value):
    """Валидация форматов файлов"""
    if value.name.endswith in ['.pdf', '.fb2', '.mobi', '.epub']:
        raise ValidationError(
            u'Загрузите файл формата pdf, fb2, mobi или epub')
