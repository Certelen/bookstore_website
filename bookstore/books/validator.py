from django.core.exceptions import ValidationError


def book_directory_path(instance, filename):
    return f'books_file/{instance.book.name}/{filename}'


def validate_file(value):
    if value.name.endswith in ['.pdf', '.fb2', '.mobi', '.epub']:
        raise ValidationError(
            u'Загрузите файл формата pdf, fb2, mobi или epub')
