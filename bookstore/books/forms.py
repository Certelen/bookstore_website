from django import forms


class SearchForm(forms.Form):
    search_word = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Поиск'}), required=False)
