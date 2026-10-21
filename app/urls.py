from django.urls import path, include
from .views import (
    book_list,
    book_detail,
    book_create,
    book_update,
    book_delete,
    dashboard,
    user_login,
    user_logout,
    user_profile,
    user_register,
)

urlpatterns = [
    path("", book_list, name="book_list"),
    path("register/", user_register, name="register"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("profile/", user_profile, name="profile"),
    path("dashboard/", dashboard, name="dashboard"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("book/<int:id>/", book_detail, name="book_detail"),
    path("book/create/", book_create, name="book_create"),
    path("book/<int:id>/update/", book_update, name="book_update"),
    path("book/<int:id>/delete/", book_delete, name="book_delete"),
]