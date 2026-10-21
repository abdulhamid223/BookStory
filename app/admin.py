from django.contrib import admin
from .models import Book

admin.site.site_header = "BookLife admin"
admin.site.site_title = "BookLife"
admin.site.index_title = "Boshqaruv"


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "genre", "price", "published_year")
    search_fields = ("title", "author")
    list_filter = ("genre", "published_year")
    ordering = ("-published_year",)
