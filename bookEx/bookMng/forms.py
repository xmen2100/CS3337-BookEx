from django import forms
from django.forms import ModelForm
from .models import Book, BookRating


class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = [
            'name',
            'web',
            'price',
            'picture',
        ]


class RatingForm(ModelForm):
    class Meta:
        model = BookRating
        fields = ['score']
        widgets = {
            'score': forms.Select(
                choices=[(1, '1 - Poor'), (2, '2 - Fair'), (3, '3 - Good'), (4, '4 - Very Good'), (5, '5 - Excellent')],
                attrs={'class': 'form-select'}
            )
        }
