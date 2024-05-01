import django.contrib.auth as auth
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from http import HTTPStatus
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
import uuid
from yookassa import Payment

from books.models import Genre, Book
from books.views import filter_books, forms
from .forms import SignupForm, ChangeForm
from .models import Review, Order


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
    return reverse_lazy('books:index')


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
    return reverse_lazy('books:index')


@login_required
def logout(request):
    auth.logout(request)
    return redirect('books:index')


@login_required
def favorite(request, sort='buying'):
    user = request.user
    books_list = user.favorite_books.all()
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

    favorite_books = books_list.values_list('id', flat=True)

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


@login_required
def review(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        data = request.POST
        score = int(data['score'])
        if 0 >= score > 5:
            score = 5
        Review.objects.create(
            user=request.user,
            book=book,
            comment=data['text'],
            score=score
        )
        score_list = [review.score for review in book.review.all()]
        book.score = sum(score_list) / len(score_list)
        book.save()
        return JsonResponse(status=HTTPStatus.OK, data={})
    return reverse_lazy('books:index')


@login_required
def profile(request):
    user = request.user
    change_form = ChangeForm(instance=user)
    if request.method == 'POST':
        data = request.POST
        change_form = ChangeForm(
            data=data, instance=user)
        if change_form.is_valid():
            change_form = change_form.save(commit=False)
            change_form.save()
            change_form = ChangeForm(instance=user)
    context = {
        'change_form': change_form
    }
    context.update(forms)
    return TemplateResponse(request, 'users/profile.html', context)


@login_required
def cart(request, buy=0):
    user = request.user
    order = user.order.filter(close=False)[0]
    books_order = order.book.all()
    price = sum(books_order.values_list('price', flat=True))
    context = {
        'books_order': books_order,
        'price': price,
        'buy': buy
    }
    context.update(forms)
    return TemplateResponse(request, 'users/cart.html', context)


@login_required
def payment(request):
    user = request.user
    order = user.order.filter(close=False)[0]
    if order.payment:
        if 'succeeded' == Payment.find_one(order.payment).status:
            for book in order.book.all():
                user.buyed_books.add(book)
            order.close = True
            Order.objects.create(user=user)
            buy = 2
        else:
            order.payment = ''
            buy = 1
        order.save()
        return redirect('users:cart', buy=buy)

    price = sum(order.book.all().values_list('price', flat=True))
    payment = Payment.create({
        "amount": {
            "value": f"{float(price)}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": 'http://127.0.0.1:8000/my/payment'
        },
        "capture": True
    }, uuid.uuid4())
    order.payment = payment.id
    order.save()
    return HttpResponseRedirect(payment.confirmation.confirmation_url)


@login_required
def library(request):
    user = request.user
    buyed_books = user.buyed_books.all()
    context = {
        'buyed_books': buyed_books
    }
    context.update(forms)
    return TemplateResponse(request, 'users/library.html', context)


@login_required
def get_book(request, book_id, format):
    user = request.user
    book = get_object_or_404(user.buyed_books, id=book_id)
    return redirect('../../../' + eval('book.files.all()[0].'+format+'.name'))
