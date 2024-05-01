from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [

    path(
        'login', views.login, name='login'
    ),
    path(
        'signup', views.signup, name='signup'
    ),
    path(
        'favorite', views.favorite, name='favorite'
    ),
    path(
        'review/<int:book_id>/', views.review, name='review'
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
        'payment', views.payment, name='payment'
    ),
    path(
        'library', views.library, name='library'
    ),
    path(
        'get_book/<int:book_id>/<str:format>', views.get_book, name='get_book'
    ),

]
