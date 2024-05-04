from django import forms


class SearchForm(forms.Form):
    search_word = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Поиск',
            'oninvalid': "this.setCustomValidity('Введите слово для поиска')",
            'oninput': "this.setCustomValidity('')"
        }))
