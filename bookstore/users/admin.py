from django.contrib import admin

from .models import CustomUser, Order, Review, ViewedGenres


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(ViewedGenres)
class ViewedGenresAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass
