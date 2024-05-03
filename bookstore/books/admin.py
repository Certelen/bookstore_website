from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError


from .models import Book, Genre, Banner, BookFiles, Event


class BookFilesInline(admin.TabularInline):
    model = BookFiles
    extra = 1
    min_num = 1


class EventForm(forms.ModelForm):
    def clean(self):
        data = self.cleaned_data
        if 'event_on' not in data:
            raise ValidationError(
                'Укажите цель акции'
            )
        event_on = data['event_on']
        if event_on == 'genres':
            for genre in data['genres']:
                data['books'] = genre.books.all()
        if event_on == 'all_books':
            data['books'] = Book.objects.all()


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    inlines = [BookFilesInline]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    exclude = []
    form = EventForm

    def has_change_permission(self, request, obj=None):
        return False

    def get_form(self, request, obj=None, change=False, **kwargs):
        self.exclude = []
        if obj is not None:
            exclude = ['books', 'genres', 'all_books']
            for index in range(3):
                if obj.event_on == exclude[index]:
                    exclude.pop(index)
                    self.exclude += exclude
                    break
        return super(EventAdmin, self).get_form(request, obj, **kwargs)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    pass
