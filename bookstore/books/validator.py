from django.core.exceptions import ValidationError


def book_directory_path(instance, filename):
    return f'books_file/{instance.book.name}/{filename}'


def validate_file_pdf(value):
    if not value.name.endswith('.pdf'):
        raise ValidationError(u'Загрузите файл формата pdf')


def validate_file_fb2(value):
    if not value.name.endswith('.fb2'):
        raise ValidationError(u'Загрузите файл формата pdf')


def validate_file_epub(value):
    if not value.name.endswith('.epub'):
        raise ValidationError(u'Загрузите файл формата epub')


def validate_file_mobi(value):
    if not value.name.endswith('.mobi'):
        raise ValidationError(u'Загрузите файл формата mobi')
