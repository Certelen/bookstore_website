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
]
