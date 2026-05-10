from django.contrib import admin

from .models import Book, BookRating, Favorite, MainMenu

admin.site.register(MainMenu)
admin.site.register(Book)
admin.site.register(BookRating)
admin.site.register(Favorite)
