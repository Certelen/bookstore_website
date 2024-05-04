from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [

    path(
        'login', views.login, name='login'
    ),
    path(
        'logout', views.logout, name='logout'
    ),
    path(
        'signup', views.signup, name='signup'
    ),
    path(
        'favorite', views.favorite, name='favorite'
    ),
    path(
        'review/<int:book_id>/', views.create_review, name='review'
    ),
    path(
        'review/<int:book_id>/<int:review_id>/',
        views.change_review,
        name='change_review'
    ),
    path(
        'profile', views.profile, name='profile'
    ),
    path(
        'cart', views.cart, name='cart'
    ),
    path(
        'cart/<int:buy>/', views.cart, name='cart'
    ),
    path(
        'take_cart_img', views.take_cart_img, name='take_cart_img'
    ),
    path(
        'payment', views.payment, name='payment'
    ),
    path(
        'library', views.library, name='library'
    ),
    path(
        'get_book/<int:book_id>/<str:format>', views.get_book, name='get_book'
    ),
]
