from django.template.response import TemplateResponse
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from datetime import timedelta, date
from itertools import chain

from .models import Book, Genre, Banner
from .forms import SearchForm
from users.models import Review, ViewedGenres
from users.forms import SignupForm
from bookstore.settings import NEWBOOK_DAYS, MAX_BOOKS_ON_SLIDER


def main_forms(request, order_full=False):
    """Формы ниже используется на всех страницах"""
    user = request.user
    search_form = SearchForm
    auth_form = AuthenticationForm
    signup_form = SignupForm(auto_id='signup_%s')
    if user.is_authenticated:
        order_full = user.order.get(close=False).book.all().exists()

    forms = {
        'search_form': search_form,
        'auth_form': auth_form,
        'signup_form': signup_form,
        'order_full': order_full
    }
    return forms


def filter_books(books_list, data, sort):
    """
    Фильтрация книг
    books_list - список книг,
    data - requst.POST из родительской функции,
    sort - способ сортировки,
    """
    if data.getlist('genres'):
        books_list = books_list.filter(
            genre=data.getlist('genres').pop()
        )
        for search_genre in data.getlist('genres'):
            books_list = books_list.filter(genre=search_genre)
    if data.get('pricemin', '') or data.get('pricemax', ''):
        books_list = books_list.annotate(
            total_price=(F('price') * (100 - F('discount'))) / 100
        ).filter(total_price__range=(
            int(data['pricemin']) if data['pricemin'] else 0,
            int(data['pricemax']) if data['pricemax'] else 9999990
        ))
    if data.get('datemin', '') or data.get('datemax', ''):
        books_list = books_list.filter(created__range=(
            data['datemin'] if data['datemin'] else date(1000, 1, 1),
            data['datemax'] if data['datemax'] else date(9999, 1, 1)
        ))
    return books_list


def catalog_type(request, books_list, sort, auth=False, favorite=False):
    """
    Сортировка и фильтрация для каталог-подобных страниц
    request - request из родительской функции,
    books_list - список книг,
    sort - способ сортировки,
    auth - для родительской функции требуется авторизация (@login_required),
    favorite - список избранного = список книг
    """
    data = request.POST
    user = request.user
    filter_dict = {
        'sort': sort
    }
    favorite_books = []
    if request.method == "POST" and books_list and 'apply_filter' in data:
        sort = data.get('sort', sort)
        books_list = filter_books(books_list, data, sort)
        post_filter_dict = {
            'genres': list(map(int, data.getlist('genres'))),
            'pricemin': data.get('pricemin', ''),
            'pricemax': data.get('pricemax', ''),
            'datemin': data.get('datemin', ''),
            'datemax': data.get('datemax', ''),
        }
        filter_dict.update(post_filter_dict)

    if (not auth and user.is_authenticated) or auth:
        favorite_books = user.favorite_books.all().values_list('id', flat=True)
    elif favorite:
        favorite_books = books_list

    if books_list and sort:
        books_list = books_list.annotate(
            total_price=(F('price') * (100 - F('discount'))) / 100
        ).order_by(
            '-' + sort[4:] if 'min_' in sort else sort
        )
    context = {
        'page_obj': books_list,
        'genres': Genre.objects.all(),
        sort: 'active',
        'filter_dict': filter_dict,
        'favorite_books': favorite_books
    }
    context.update(main_forms(request))
    return context


def index(request):
    """Главная"""
    user = request.user
    popular = Book.objects.all().order_by('-buying')
    new = Book.objects.filter(
        created__gte=date.today() - timedelta(days=NEWBOOK_DAYS))
    recomended = Book.objects.all().order_by('-score')
    favorite_books = None

    if not new:
        new = Book.objects.order_by('created')

    if user.is_authenticated:
        if user.viewed_genres:
            user_recomended = popular.filter(genre=user.most_viewed_genres)
            recomended = list(chain(user_recomended,
                              recomended.difference(user_recomended)))
        favorite_books = user.favorite_books.all().values_list('id', flat=True)

    context = {
        'popular': popular[:MAX_BOOKS_ON_SLIDER],
        'new': new[:MAX_BOOKS_ON_SLIDER],
        'recomended': recomended[:MAX_BOOKS_ON_SLIDER],
        'banners': Banner.objects.all(),
        'favorite_books': favorite_books
    }
    context.update(main_forms(request))
    return TemplateResponse(request, 'index.html', context)


def search(request, sort=''):
    """Поиск"""
    search_form = SearchForm
    data = request.POST
    search_word = data.get('search_word', '')
    books_list = Book.objects.all()
    sort = data.get('sort', '')
    if search_word:
        if not sort:
            books_name_list = Book.objects.filter(
                name__iregex=search_word
            ).order_by('-buying')
            books_author_list = Book.objects.filter(
                author__iregex=search_word
            ).order_by('-buying')
            books_list = list(chain(books_name_list, books_author_list))
        else:
            books_list = Book.objects.filter(
                Q(description__iregex=search_word) |
                Q(author__iregex=search_word) |
                Q(name__iregex=search_word)
            )
        search_form = SearchForm(data=data)

    context = catalog_type(request, books_list, sort)
    context['search_form'] = search_form
    return TemplateResponse(request, 'books/search.html', context)


def catalog(request, sort='min_buying'):
    """Основной каталог"""
    books_list = Book.objects.all()
    context = catalog_type(request, books_list, sort)
    return TemplateResponse(request, 'books/catalog.html', context)


def news(request, sort='min_release'):
    """Каталог новых книг"""
    books_list = Book.objects.filter(
        created__gte=date.today() - timedelta(days=NEWBOOK_DAYS))
    context = catalog_type(request, books_list, sort)
    return TemplateResponse(request, 'books/news.html', context)


def book_detail(request, book_id, book_status=0, book_favorite=0):
    """Страница книги"""
    user = request.user
    book = get_object_or_404(Book, id=book_id)
    files_format = book.files.all().values_list('name', flat=True)

    if user.is_authenticated:
        order = user.order.filter(close=False)[0]
        book_status = 2 if user.buyed_books.filter(id=book_id) else 0
        if not book_status:
            book_status = 1 if order.book.filter(id=book_id) else 0
        book_favorite = 1 if user.favorite_books.filter(id=book_id) else 0
        for genre in book.genre.all():
            ViewedGenres.objects.create(user=user, genre=genre)

    reviews = Review.objects.filter(book=book)
    user_have_review = reviews.filter(user=user).exists()
    context = {
        'book': book,
        'book_status': book_status,
        'reviews': reviews,
        'book_favorite': book_favorite,
        'files_format': files_format,
        'user_have_review': user_have_review
    }
    context.update(main_forms(request))
    return TemplateResponse(request, 'books/book_detail.html', context)


@login_required
def change_favorite(request, book_favorite=0):
    """Добавление или удаление из избранного на карточках и странице товара"""
    if request.method == "POST":
        user = request.user
        book = Book.objects.get(id=request.POST['book'])
        favorite_books = user.favorite_books.all().filter(id=book.id)
        if favorite_books:
            user.favorite_books.remove(book)
        else:
            user.favorite_books.add(book)
            book_favorite = 1
        context = {
            'book': book,
            'book_favorite': book_favorite,
        }
        if 'button' in request.POST:
            return TemplateResponse(
                request, 'dynamic_forms/favorite_button.html', context
            )
        return TemplateResponse(
            request, 'dynamic_forms/favorite.html', context
        )
    return reverse_lazy('books:index')


@login_required
def change_cart(request, book_status=0):
    """Добавление или удаление из корзины на странице товара"""
    if request.method == "POST":
        user = request.user
        book = get_object_or_404(Book, id=request.POST['book'])
        if user.buyed_books.filter(id=book.id):
            context = {
                'book': book,
                'book_status': 2
            }
            return TemplateResponse(
                request, 'dynamic_forms/cart_button.html', context
            )
        order = user.order.filter(close=False)[0]
        if order.book.filter(id=book.id):
            order.book.remove(book)
        else:
            book_status = 1
            order.book.add(book)
        context = {
            'book': book,
            'book_status': book_status
        }
        return TemplateResponse(
            request, 'dynamic_forms/cart_button.html', context
        )
    return reverse_lazy('books:index')
