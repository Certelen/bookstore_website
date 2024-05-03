from csv import DictReader
from django.core.management import BaseCommand
from django.core.files.images import ImageFile
import datetime

from books.models import Book, Genre, Banner


class Command(BaseCommand):
    """Загрузка данных из static/data в базу данных"""
    help = "Loads data from csv files in static/data"

    def handle(self, *args, **options):

        for genre in DictReader(
            open('static/data/genres.csv', encoding="utf8")
        ):
            genre = Genre(
                id=genre['id'],
                name=genre['name']
            )
            genre.save()

        for book in DictReader(
            open('static/data/books.csv', encoding="utf8")
        ):
            new_book = Book(
                id=book['id'],
                name=book['name'],
                author=book['author'],
                pages=book['pages'],
                description=book['description'],
                main_image=ImageFile(
                    open(f"static/data/img/{book['id']}.png", "rb")),
                price=book['price'],
                score=book['score'],
                release=datetime.datetime.strptime(
                    book['release'], "%d%m%Y").date()
            )
            new_book.save()
            for genre in book['genre'].split(','):
                if genre:
                    genre = Genre.objects.filter(id=genre)
                    new_book.genre.add(genre[0])

        img_id = 1
        while True:
            try:
                image = ImageFile(
                    open(f"static/data/banners/{img_id}.png", "rb"))
            except Exception:
                break
            new_banner = Banner(
                id=img_id,
                image=image
            )
            new_banner.save()
            img_id += 1
