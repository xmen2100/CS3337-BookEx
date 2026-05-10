from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.db.utils import OperationalError, ProgrammingError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView

from .forms import BookForm, RatingForm
from .models import Book, BookRating, Favorite, MainMenu


def get_menu_items():
    menu_items = list(MainMenu.objects.all())
    if menu_items:
        return menu_items
    return [
        {'item': 'Home', 'link': '/'},
        {'item': 'About Us', 'link': '/aboutus'},
        {'item': 'Browse Books', 'link': '/displaybooks'},
        {'item': 'Post Book', 'link': '/postbook'},
        {'item': 'My Books', 'link': '/mybooks'},
        {'item': 'Favorites', 'link': '/favorites'},
        {'item': 'Cart', 'link': '/cart'},
    ]


def add_picture_paths(books):
    for book in books:
        try:
            book.pic_path = book.picture.url[21:]
        except Exception:
            book.pic_path = 'uploads/cover.jpg'
    return books


def safe_favorite_ids(user):
    if not getattr(user, 'is_authenticated', False):
        return []
    try:
        return list(Favorite.objects.filter(user=user).values_list('book_id', flat=True))
    except (OperationalError, ProgrammingError):
        return []


def safe_user_ratings(user):
    if not getattr(user, 'is_authenticated', False):
        return {}
    try:
        return {r.book_id: r.score for r in BookRating.objects.filter(user=user)}
    except (OperationalError, ProgrammingError):
        return {}


def safe_user_rating_for_book(book, user):
    if not getattr(user, 'is_authenticated', False):
        return None
    try:
        return BookRating.objects.filter(book=book, user=user).first()
    except (OperationalError, ProgrammingError):
        return None


def get_cart(request):
    return request.session.setdefault('cart', [])


def cart_book_objects(request):
    cart_ids = get_cart(request)
    books = Book.objects.filter(id__in=cart_ids)
    ordered_books = []
    for book_id in cart_ids:
        for book in books:
            if book.id == book_id:
                ordered_books.append(book)
                break
    return add_picture_paths(ordered_books)


def index(request):
    featured_books = add_picture_paths(Book.objects.all().order_by('-id')[:3])
    return render(
        request,
        'bookMng/index.html',
        {
            'item_list': get_menu_items(),
            'featured_books': featured_books,
        },
    )


def aboutus(request):
    return render(
        request,
        'bookMng/aboutus.html',
        {
            'item_list': get_menu_items(),
        },
    )


@login_required
def postbook(request):
    submitted = False
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.username = request.user
            book.save()
            return HttpResponseRedirect('/postbook?submitted=True')
    else:
        form = BookForm()
        if 'submitted' in request.GET:
            submitted = True
    return render(
        request,
        'bookMng/postbook.html',
        {
            'form': form,
            'item_list': get_menu_items(),
            'submitted': submitted,
        },
    )


def displaybooks(request):
    query = request.GET.get('q', '').strip()
    books = Book.objects.all().order_by('-id')
    if query:
        books = books.filter(Q(name__icontains=query) | Q(username__username__icontains=query))
    books = add_picture_paths(list(books))

    favorite_ids = safe_favorite_ids(request.user)
    user_ratings = safe_user_ratings(request.user)

    for book in books:
        book.user_rating = user_ratings.get(book.id)

    return render(
        request,
        'bookMng/displaybooks.html',
        {
            'item_list': get_menu_items(),
            'books': books,
            'query': query,
            'favorite_ids': favorite_ids,
            'user_ratings': user_ratings,
        },
    )


class Register(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('register-success')

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.success_url)


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    add_picture_paths([book])
    favorite_ids = safe_favorite_ids(request.user)
    user_rating = safe_user_rating_for_book(book, request.user)

    return render(
        request,
        'bookMng/book_detail.html',
        {
            'item_list': get_menu_items(),
            'book': book,
            'favorite_ids': favorite_ids,
            'user_rating': user_rating,
            'rating_form': RatingForm(initial={'score': user_rating.score if user_rating else 5}),
        },
    )


@login_required
def mybooks(request):
    books = add_picture_paths(list(Book.objects.filter(username=request.user).order_by('-id')))
    return render(
        request,
        'bookMng/mybooks.html',
        {
            'item_list': get_menu_items(),
            'books': books,
        },
    )


@login_required
def book_delete(request, book_id):
    book = get_object_or_404(Book, id=book_id, username=request.user)
    book.delete()
    return render(
        request,
        'bookMng/book_delete.html',
        {
            'item_list': get_menu_items(),
        },
    )


@login_required
def rate_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        score = int(request.POST.get('score', 5))
        try:
            BookRating.objects.update_or_create(book=book, user=request.user, defaults={'score': score})
        except (OperationalError, ProgrammingError):
            pass
    return redirect(reverse('book_detail', args=[book_id]))


@login_required
def toggle_favorite(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    try:
        favorite = Favorite.objects.filter(book=book, user=request.user).first()
        if favorite:
            favorite.delete()
        else:
            Favorite.objects.create(book=book, user=request.user)
    except (OperationalError, ProgrammingError):
        pass
    return redirect(request.META.get('HTTP_REFERER', reverse('displaybooks')))


@login_required
def favorites(request):
    try:
        books = Book.objects.filter(favorite__user=request.user).distinct().order_by('-favorite__created_at')
        books = add_picture_paths(list(books))
    except (OperationalError, ProgrammingError):
        books = []
    return render(
        request,
        'bookMng/favorites.html',
        {
            'item_list': get_menu_items(),
            'books': books,
        },
    )


def add_to_cart(request, book_id):
    get_object_or_404(Book, id=book_id)
    cart = get_cart(request)
    if book_id not in cart:
        cart.append(book_id)
        request.session['cart'] = cart
        request.session.modified = True
    return redirect(request.META.get('HTTP_REFERER', reverse('displaybooks')))


def remove_from_cart(request, book_id):
    cart = get_cart(request)
    if book_id in cart:
        cart.remove(book_id)
        request.session['cart'] = cart
        request.session.modified = True
    return redirect(reverse('cart'))


def cart(request):
    books = cart_book_objects(request)
    total = sum((book.price for book in books), Decimal('0.00'))
    return render(
        request,
        'bookMng/cart.html',
        {
            'item_list': get_menu_items(),
            'books': books,
            'total': total,
        },
    )
