from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "price", "published_year")
    search_fields = ("title", "author")
    list_filter = ("published_year",)
    ordering = ("-published_year",)
