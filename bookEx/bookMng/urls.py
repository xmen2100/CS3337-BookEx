from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('aboutus', views.aboutus, name='aboutus'),
    path('postbook', views.postbook, name='postbook'),
    path('displaybooks', views.displaybooks, name='displaybooks'),
    path('book_detail/<int:book_id>', views.book_detail, name='book_detail'),
    path('mybooks', views.mybooks, name='mybooks'),
    path('book_delete/<int:book_id>', views.book_delete, name='book_delete'),
    path('rate/<int:book_id>', views.rate_book, name='rate_book'),
    path('favorite/<int:book_id>', views.toggle_favorite, name='toggle_favorite'),
    path('favorites', views.favorites, name='favorites'),
    path('cart', views.cart, name='cart'),
    path('cart/add/<int:book_id>', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:book_id>', views.remove_from_cart, name='remove_from_cart'),
]
