from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


GENRES = [
    ("badiiy", "Badiiy"),
    ("psixologiya", "Psixologiya"),
    ("tarixiy", "Tarixiy"),
    ("ertak", "Ertak"),
    ("ilmiy", "Ilmiy"),
    ("biznes", "Biznes"),
    ("detektiv", "Detektiv"),
    ("fantastika", "Fantastika"),
    ("sheriyat", "She'riyat"),
]

GENRE_LABELS = {
    "uz": dict(GENRES),
    "ru": {
        "badiiy": "Художественная", "psixologiya": "Психология", "tarixiy": "Историческая",
        "ertak": "Сказки", "ilmiy": "Научная", "biznes": "Бизнес",
        "detektiv": "Детектив", "fantastika": "Фантастика", "sheriyat": "Поэзия",
    },
    "en": {
        "badiiy": "Fiction", "psixologiya": "Psychology", "tarixiy": "History",
        "ertak": "Fairy tales", "ilmiy": "Science", "biznes": "Business",
        "detektiv": "Detective", "fantastika": "Sci-fi", "sheriyat": "Poetry",
    },
}


class Book(models.Model):
    title = models.CharField("Kitob nomi", max_length=150)
    author = models.CharField("Muallif", max_length=100)
    price = models.DecimalField("Narx", max_digits=10, decimal_places=2)
    genre = models.CharField("Janr", max_length=20, choices=GENRES, default="badiiy")
    description = models.TextField("Tavsif", blank=True, null=True)
    published_year = models.PositiveIntegerField("Nashr yili")

    image = models.ImageField(
        "Rasm",
        upload_to="books/"
    )

    class Meta:
        verbose_name = "Kitob"
        verbose_name_plural = "Kitoblar"

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="Foydalanuvchi")
    phone = models.CharField("Telefon", max_length=20, blank=True, null=True)
    address = models.CharField("Manzil", max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profillar"

    def __str__(self):
        return self.user.username