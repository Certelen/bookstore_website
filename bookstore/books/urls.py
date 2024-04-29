from django.urls import path

from . import views

app_name = 'books'

urlpatterns = [
    path(
        '', views.index, name='index'
    ),
    path(
        'catalog', views.catalog, name='catalog'
    ),
    path(
        'news', views.news, name='news'
    ),
    path(
        'change_favorite', views.change_favorite, name='change_favorite'
    ),
    path(
        'change_cart', views.change_cart, name='change_cart'
    ),
    path(
        'search', views.search, name='search'
    ),
    path(
        'book/<int:book_id>/', views.book_detail, name='book'
    ),

]
