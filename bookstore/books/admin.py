from django.contrib import admin

from .models import Book, Genre, BookImage, Banner, BookFiles


class BookFilesInline(admin.TabularInline):
    model = BookFiles
    extra = 1
    can_delete = False
    min_num = 1
    max_num = 1


class BookImageInline(admin.TabularInline):
    model = BookImage
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    inlines = [BookFilesInline, BookImageInline]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    pass
