from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Profile
from app.forms import BookForm, UserProfileForm, UserRegisterForm

User = get_user_model()


def user_register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            cleaned = form.cleaned_data
            last_user = User.objects.order_by("-id").first()
            next_id = (last_user.id + 1) if last_user else 1
            username = str(next_id)

            user = User.objects.create_user(
                username=username,
                password=cleaned["password"],
                first_name=cleaned["first_name"],
                last_name=cleaned["last_name"],
            )

            Profile.objects.create(
                user=user,
                phone=cleaned["phone"],
                address=cleaned["address"],
            )

            login(request, user)
            messages.success(request, "Your account has been created successfully.")
            return redirect("book_list")
    else:
        form = UserRegisterForm()

    return render(request, "register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        password = request.POST.get("password")
        next_url = request.POST.get("next") or "book_list"

        user = None
        if user_id:
            try:
                user = User.objects.get(id=int(user_id))
            except (ValueError, User.DoesNotExist):
                user = User.objects.filter(username=str(user_id)).first()

        auth_user = authenticate(request, username=user.username if user else None, password=password)

        if auth_user is not None:
            login(request, auth_user)
            return redirect(next_url)

        messages.error(request, "User ID or password is incorrect.")

    next_url = request.GET.get("next", "")
    return render(request, "login.html", {"next": next_url})


def user_logout(request):
    logout(request)
    return redirect("book_list")


@login_required(login_url="login")
def user_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST)

        if form.is_valid():
            request.user.first_name = form.cleaned_data["first_name"]
            request.user.last_name = form.cleaned_data["last_name"]
            request.user.save()

            profile.phone = form.cleaned_data["phone"]
            profile.address = form.cleaned_data["address"]
            profile.save()

            messages.success(request, "Profile updated.")
            return redirect("book_list")
    else:
        form = UserProfileForm(initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "phone": profile.phone,
            "address": profile.address,
        })

    return render(request, "profile.html", {"form": form, "profile": profile})


def book_list(request):
    books = Book.objects.all().order_by("-id")

    return render(request, "book_list.html", {
        "books": books
    })


def book_detail(request, id):
    book = get_object_or_404(Book, id=id)

    return render(request, "book_detail.html", {
        "book": book
    })


@login_required(login_url="login")
def book_create(request):
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect("book_list")
    else:
        form = BookForm()

    return render(request, "book_create.html", {
        "form": form
    })


@login_required(login_url="login")
def book_update(request, id):
    if not request.user.is_staff:
        raise PermissionDenied

    book = get_object_or_404(Book, id=id)

    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)

        if form.is_valid():
            form.save()
            return redirect("book_list")
    else:
        form = BookForm(instance=book)

    return render(request, "book_update.html", {
        "form": form,
        "book": book
    })


@login_required(login_url="login")
def book_delete(request, id):
    if not request.user.is_staff:
        raise PermissionDenied

    book = get_object_or_404(Book, id=id)
    book.delete()

    return redirect("book_list")