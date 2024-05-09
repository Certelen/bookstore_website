import django.contrib.auth as auth
from django.template.response import TemplateResponse
from django.db.models import F
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from http import HTTPStatus
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
import uuid
from yookassa import Payment

from books.models import Book
from books.views import catalog_type, main_forms
from .forms import SignupForm, ChangeForm
from .models import Review, Order


def signup(request):
    """Регистрация"""
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
    """Вход в аккаунт"""
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
    """Выход из аккаунта"""
    auth.logout(request)
    return redirect('books:index')


@login_required
def favorite(request, sort='buying'):
    """Каталог избранного"""
    books_list = request.user.favorite_books.all()
    context = catalog_type(request, books_list, sort, True, True)
    return TemplateResponse(request, 'users/favorite.html', context)


@login_required
def create_review(request, book_id):
    """Создание нового отзыва"""
    book = get_object_or_404(Book, id=book_id)
    user = request.user
    if request.method == 'POST' and not book.review.filter(user=user).exists():
        data = request.POST
        score = int(data['score'])
        if 0 >= score > 5:
            score = 5
        Review.objects.create(
            user=user,
            book=book,
            comment=data['text'],
            score=score
        )
        if book.review.all():
            score_list = [review.score for review in book.review.all()]
            book.score = sum(score_list) / len(score_list)
            book.save()
        return JsonResponse(status=HTTPStatus.OK, data={})
    return redirect('books:book', book_id=book_id)


@login_required
def change_review(request, book_id, review_id):
    """Изменение или удаление отзыва"""
    book = get_object_or_404(Book, id=book_id)
    review = Review.objects.filter(id=review_id)
    if request.method == 'POST' and review:
        data = request.POST
        if 'delete' in data:
            review.delete()
        else:
            score = int(data['score'])
            if 0 >= score > 5:
                score = 5
            review.update(
                comment=data['text'],
                score=score
            )
        if book.review.all():
            score_list = [review.score for review in book.review.all()]
            book.score = sum(score_list) / len(score_list)
        else:
            book.score = 0
        book.save()
    return redirect('books:book', book_id=book_id)


@login_required
def profile(request):
    """Профиль"""
    user = request.user
    change_form = ChangeForm(instance=user)
    if request.method == 'POST':
        data = request.POST
        change_form = ChangeForm(
            data=data, instance=user)
        if change_form.is_valid():
            change_form = change_form.save(commit=False)
            change_form.save()
            if data['password']:
                user.set_password(data['password'])
                user.save()
            return redirect('books:index')
    context = {
        'change_form': change_form
    }
    context.update(main_forms(request))
    return TemplateResponse(request, 'users/profile.html', context)


@login_required
def cart(request, buy=0):
    """Корзина.
    buy влияет на вывод модального окна после оплаты:
    0 - пользователь не перенаправлен с оплаты,
    1 - пользователь вернулся с оплаты не оплатив,
    2 - пользователь вернулся с оплаты оплатив"""
    books_order = request.user.order.get(close=False).book.all()
    price = sum(books_order.annotate(
        total_price=(F('price') * (100 - F('discount'))) / 100
    ).values_list('total_price', flat=True))
    context = {
        'books_order': books_order,
        'price': price,
        'buy': buy
    }
    context.update(main_forms(request))
    return TemplateResponse(request, 'users/cart.html', context)


def take_cart_img(request, order_full=False):
    if request.user.is_authenticated:
        order_full = request.user.order.get(close=False).book.all().exists()
    return TemplateResponse(
        request, 'includes/cart_img.html', {'order_full': order_full}
    )


@login_required
def payment(request):
    """Процесс оплаты и проверка что оплата успешна.
    id платежа встраивается в order.
    Если оплата неуспешна, id удаляется и создается новая оплата"""
    user = request.user
    order = user.order.filter(close=False)[0]
    if order.payment:
        if 'succeeded' == Payment.find_one(order.payment).status:
            for book in order.book.all():
                user.buyed_books.add(book)
            order.close = True
            Order.objects.create(user=user)
            book.buying += 1
            book.save()
            buy = 2
        else:
            order.payment = ''
            buy = 1
        order.save()
        return redirect('users:cart', buy=buy)

    price = sum(order.book.annotate(
        total_price=(F('price') * (100 - F('discount'))) / 100
    ).values_list('total_price', flat=True))
    payment = Payment.create({
        "amount": {
            "value": f"{float(price)}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": 'http://dch02arv.beget.tech/my/payment'
        },
        "capture": True
    }, uuid.uuid4())
    order.payment = payment.id
    order.save()
    return HttpResponseRedirect(payment.confirmation.confirmation_url)


@login_required
def library(request):
    """Купленные книги пользователя (библиотека)"""
    context = {
        'buyed_books': request.user.buyed_books.all()
    }
    context.update(main_forms(request))
    return TemplateResponse(request, 'users/library.html', context)


@login_required
def get_book(request, book_id, format):
    """Возвращаем ссылку на запрашиваемый формат файла"""
    book = get_object_or_404(request.user.buyed_books, id=book_id)
    return redirect('../../../' + book.files.all().get(name=format).file.url)
