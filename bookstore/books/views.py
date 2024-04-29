from django.template.response import TemplateResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from datetime import timedelta, date

from .models import Book, Genre, Banner
from .forms import SearchForm
from users.models import Review
from users.forms import SignupForm
# from bookstore.settings import (MAX_ROW_ON_PAGE,
# NEWBOOK_DAYS, MAX_BOOKS_ON_SLIDER)


# Формы ниже используется на всех страницах
search_form = SearchForm
auth_form = AuthenticationForm
signup_form = SignupForm(auto_id='signup_%s')

forms = {
    'search_form': search_form,
    'auth_form': auth_form,
    'signup_form': signup_form
}


def filter_books(books_list, data, sort):
    if data.getlist('genres'):
        books_list = books_list.filter(
            genre=data.getlist('genres').pop()
        )
        for search_genre in data.getlist('genres'):
            books_list = books_list.filter(genre=search_genre)
    if data['pricemin'] or data['pricemax']:
        books_list = books_list.filter(price__range=(
            int(data['pricemin']) if data['pricemin'] else 0,
            int(data['pricemax']) if data['pricemax'] else 9999990
        ))
    if data['datemin'] or data['datemax']:
        books_list = books_list.filter(created__range=(
            data['datemin'] if data['datemin'] else date(1000, 1, 1),
            data['datemax'] if data['datemax'] else date(9999, 1, 1)
        ))
    return books_list


def index(request):
    user = request.user
    popular = Book.objects.all().order_by('-buying')
    new = Book.objects.filter(created__gte=date.today() - timedelta(days=7))
    if not new:
        new = Book.objects.order_by('created')
    if user.is_authenticated:
        if user.viewed_genres:
            recomended = popular.filter(genre=user.most_viewed_genres)
        recomended = Book.objects.all().order_by('-score')
        favorite_books = user.favorite_books.all().values_list('id', flat=True)

    context = {
        'popular': popular[:15],
        'new': new[:15],
        'recomended': recomended[:15],
        'banners': Banner.objects.all(),
        'favorite_books': favorite_books
    }
    context.update(forms)
    return TemplateResponse(request, 'index.html', context)


def search(request, sort='buying'):
    search_form = SearchForm
    user = request.user
    data = request.POST
    filter_dict = {}
    books_list = []
    if request.method == 'POST':
        if data['search_word']:
            books_list = Book.objects.filter(
                Q(description__iregex=data['search_word']) |
                Q(author__iregex=data['search_word']) |
                Q(name__iregex=data['search_word'])
            )
            search_form = SearchForm(data=data)
        sort = data.get('sort', sort)
        filter_dict = {
            'sort': sort
        }
        if 'pricemin' in data:
            books_list = filter_books(books_list, data, sort)
            post_filter_dict = {
                'genres': list(map(int, data.getlist('genres'))),
                'pricemin': data['pricemin'],
                'pricemax': data['pricemax'],
                'datemin': data['datemin'],
                'datemax': data['datemax'],
            }
            filter_dict.update(post_filter_dict)
        if sort:
            books_list = books_list.order_by(
                '-' + sort[4:] if 'min_' in sort else sort
            )

    if user.is_authenticated:
        favorite_books = user.favorite_books.all().values_list('id', flat=True)

    genres = Genre.objects.all()
    context = {
        'page_obj': books_list,
        'genres': genres,
        sort: 'active',
        'filter_dict': filter_dict,
        'favorite_books': favorite_books,
    }
    context.update(forms)
    context['search_form'] = search_form
    return TemplateResponse(request, 'books/search.html', context)


def catalog(request, sort='buying'):
    user = request.user
    books_list = Book.objects.all()
    filter_dict = {
        'sort': sort
    }
    if request.method == "POST":
        data = request.POST
        sort = data['sort']
        books_list = filter_books(books_list, data, sort)
        post_filter_dict = {
            'genres': list(map(int, data.getlist('genres'))),
            'pricemin': data['pricemin'],
            'pricemax': data['pricemax'],
            'datemin': data['datemin'],
            'datemax': data['datemax'],
        }
        filter_dict.update(post_filter_dict)

    if user.is_authenticated:
        favorite_books = user.favorite_books.all().values_list('id', flat=True)
    genres = Genre.objects.all()
    books_list = books_list.order_by(
        '-' + sort[4:] if 'min_' in sort else sort
    )
    context = {
        'page_obj': books_list,
        'genres': genres,
        sort: 'active',
        'filter_dict': filter_dict,
        'favorite_books': favorite_books
    }
    context.update(forms)
    return TemplateResponse(request, 'books/catalog.html', context)


def news(request, sort='min_created'):
    user = request.user
    books_list = Book.objects.filter(
        created__gte=date.today() - timedelta(days=7))
    filter_dict = {
        'sort': sort
    }
    if request.method == "POST":
        data = request.POST
        sort = data['sort']
        books_list = filter_books(books_list, data, sort)
        post_filter_dict = {
            'genres': list(map(int, data.getlist('genres'))),
            'pricemin': data['pricemin'],
            'pricemax': data['pricemax'],
            'datemin': data['datemin'],
            'datemax': data['datemax'],
        }
        filter_dict.update(post_filter_dict)

    if user.is_authenticated:
        favorite_books = user.favorite_books.all().values_list('id', flat=True)

    genres = Genre.objects.all()
    books_list = books_list.order_by(
        '-' + sort[4:] if 'min_' in sort else sort
    )
    context = {
        'page_obj': books_list,
        'genres': genres,
        sort: 'active',
        'filter_dict': filter_dict,
        'favorite_books': favorite_books
    }
    context.update(forms)
    return TemplateResponse(request, 'books/news.html', context)


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    images = [book.main_image]
    images += [obj.image for obj in book.images.all()]
    if request.user.is_authenticated:
        order = get_object_or_404(request.user.order, close=False)
        book_order = order.book.filter(book=book)
    comments = Review.objects.filter(book=book)
    context = {
        'book': book,
        'images': images,
        'book_order': bool(book_order),
        'comments': comments
    }
    context.update(forms)
    return TemplateResponse(request, 'books/book-detail.html', context)


@login_required
def change_favorite(request):
    if request.method == "POST":
        user = request.user
        book = Book.objects.get(id=request.POST['book'])
        favorite_books = user.favorite_books.all()
        favorite_books = favorite_books.filter(id=book.id)
        if favorite_books:
            user.favorite_books.remove(book)
        else:
            user.favorite_books.add(book)
        favorite_books = favorite_books.values_list(flat=True)
        context = {
            'book': book,
            'favorite_books': favorite_books
        }
        return TemplateResponse(
            request, 'dynamic_forms/favorite.html', context
        )
    return reverse_lazy('books:index')
