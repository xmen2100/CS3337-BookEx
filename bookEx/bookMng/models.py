from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.utils import OperationalError, ProgrammingError


class MainMenu(models.Model):
    item = models.CharField(max_length=300, unique=True)
    link = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return self.item


class Book(models.Model):
    name = models.CharField(max_length=200)
    web = models.URLField(max_length=300)
    price = models.DecimalField(decimal_places=2, max_digits=8)
    publishdate = models.DateField(auto_now=True)
    picture = models.FileField(upload_to='bookEx/static/uploads')
    pic_path = models.CharField(max_length=300, editable=False, blank=True)
    username = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        try:
            ratings = list(self.bookrating_set.values_list('score', flat=True))
        except (OperationalError, ProgrammingError):
            return 0
        if not ratings:
            return 0
        return round(sum(ratings) / len(ratings), 1)

    @property
    def rating_count(self):
        try:
            return self.bookrating_set.count()
        except (OperationalError, ProgrammingError):
            return 0


class BookRating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('book', 'user')

    def __str__(self):
        return f'{self.book} - {self.user} - {self.score}'


class Favorite(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('book', 'user')

    def __str__(self):
        return f'{self.user} favorite {self.book}'
