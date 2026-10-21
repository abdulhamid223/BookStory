from django import forms
from .models import Book, GENRE_LABELS


class BookForm(forms.ModelForm):

    PLACEHOLDERS = {
        "uz": {"title": "Kitob nomi", "author": "Muallif ismi", "price": "Narx", "description": "Kitob haqida qisqacha"},
        "ru": {"title": "Название книги", "author": "Имя автора", "price": "Цена", "description": "Кратко о книге"},
        "en": {"title": "Book title", "author": "Author name", "price": "Price", "description": "Book description"},
    }

    class Meta:
        model = Book

        fields = [
            "title",
            "author",
            "price",
            "genre",
            "description",
            "published_year",
            "image",
        ]

        widgets = {
            "title": forms.TextInput(),

            "author": forms.TextInput(),

            "price": forms.NumberInput(attrs={
                "step": "0.01"
            }),

            "description": forms.Textarea(),

            "published_year": forms.NumberInput(attrs={
                "placeholder": "2026"
            }),

            "image": forms.ClearableFileInput(attrs={
                "required": True
            }),
        }

    def __init__(self, *args, lang="uz", **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = self.PLACEHOLDERS.get(lang, self.PLACEHOLDERS["en"])
        for name, text in placeholders.items():
            self.fields[name].widget.attrs["placeholder"] = text
        labels = GENRE_LABELS.get(lang, GENRE_LABELS["en"])
        self.fields["genre"].choices = [(key, labels[key]) for key, _ in self.fields["genre"].choices if key]


class UserRegisterForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    phone = forms.CharField(max_length=20)
    address = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)


class UserProfileForm(forms.Form):
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)
    phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(max_length=255, required=False)
