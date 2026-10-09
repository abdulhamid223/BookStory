from django import forms
from .models import Book


class BookForm(forms.ModelForm):

    class Meta:
        model = Book

        fields = [
            "title",
            "author",
            "price",
            "description",
            "published_year",
            "image",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Book title"
            }),

            "author": forms.TextInput(attrs={
                "placeholder": "Author name"
            }),

            "price": forms.NumberInput(attrs={
                "placeholder": "Price",
                "step": "0.01"
            }),

            "description": forms.Textarea(attrs={
                "placeholder": "Book description"
            }),

            "published_year": forms.NumberInput(attrs={
                "placeholder": "2026"
            }),

            "image": forms.ClearableFileInput(attrs={
                "required": True
            }),
        }


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
