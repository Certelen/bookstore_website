import django.contrib.auth as auth
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import JsonResponse
from http import HTTPStatus
from django.contrib.auth.forms import AuthenticationForm

from books.models import Genre
from books.views import filter_books, forms
from .forms import SignupForm


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST, auto_id='signup_%s')
        if form.is_valid():
            new_user = form.save()
            auth.login(request, new_user)
            return JsonResponse(status=HTTPStatus.OK, data={'login': True})
        context = {
            'signup_form': form
        }
        return TemplateResponse(request, 'dynamic_forms/signup.html', context)
    return reverse_lazy('products:index')


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth.login(request, form.get_user())
            return JsonResponse(status=HTTPStatus.OK, data={'login': True})
        context = {
            'auth_form': form
        }
        return TemplateResponse(request, 'dynamic_forms/auth.html', context)
    return reverse_lazy('products:index')


@login_required
def favorite(request, sort='buying'):
    user = request.user
    books_list = request.user.favorite.all()
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
    return TemplateResponse(request, 'users/favorite.html', context)
