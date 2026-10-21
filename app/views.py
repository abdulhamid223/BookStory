import math
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Profile, GENRES, GENRE_LABELS
from app.forms import BookForm, UserProfileForm, UserRegisterForm

User = get_user_model()


def tr(request, uz, ru, en):
    """Pick the message for the active language (uz / ru / en)."""
    return {"uz": uz, "ru": ru}.get(request.LANGUAGE_CODE, en)


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
            messages.success(request, tr(
                request,
                f"Hisobingiz muvaffaqiyatli yaratildi. Kirish uchun ID raqamingiz: {username}",
                f"Аккаунт успешно создан. Ваш ID для входа: {username}",
                f"Your account has been created successfully. Your login ID: {username}",
            ))
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

        messages.error(request, tr(
            request,
            "Foydalanuvchi ID yoki parol noto'g'ri.",
            "Неверный ID пользователя или пароль.",
            "User ID or password is incorrect.",
        ))

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

            messages.success(request, tr(
                request,
                "Profil ma'lumotlari saqlandi.",
                "Данные профиля сохранены.",
                "Profile updated.",
            ))
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
    counts = dict(books.values_list("genre").annotate(c=Count("id")).order_by())
    labels = GENRE_LABELS.get(request.LANGUAGE_CODE, GENRE_LABELS["en"])
    genres = [{"key": key, "label": labels[key], "count": counts.get(key, 0)} for key, _ in GENRES]

    return render(request, "book_list.html", {
        "books": books,
        "genres": genres,
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
        form = BookForm(request.POST, request.FILES, lang=request.LANGUAGE_CODE)

        if form.is_valid():
            form.save()
            return redirect("book_list")
    else:
        form = BookForm(lang=request.LANGUAGE_CODE)

    return render(request, "book_create.html", {
        "form": form
    })


@login_required(login_url="login")
def book_update(request, id):
    if not request.user.is_staff:
        raise PermissionDenied

    book = get_object_or_404(Book, id=id)

    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book, lang=request.LANGUAGE_CODE)

        if form.is_valid():
            form.save()
            return redirect("book_list")
    else:
        form = BookForm(instance=book, lang=request.LANGUAGE_CODE)

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


MONTH_NAMES = {
    "uz": ["Yan", "Fev", "Mar", "Apr", "May", "Iyn", "Iyl", "Avg", "Sen", "Okt", "Noy", "Dek"],
    "ru": ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"],
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
}


def build_chart(rows):
    """rows: list of (label, value). Adds bar heights and clean y-axis ticks."""
    peak = max([value for _, value in rows] + [1])
    raw_step = peak / 4
    magnitude = 10 ** math.floor(math.log10(raw_step)) if raw_step > 0 else 1
    step = next(s * magnitude for s in (1, 2, 5, 10) if s * magnitude >= raw_step)
    step = max(1, math.ceil(step))
    top = math.ceil(peak / step) * step

    bars = [
        {"label": label, "value": value, "pct": round(value / top * 100, 2), "is_peak": value == peak and value > 0}
        for label, value in rows
    ]
    ticks = [{"value": t, "pct": round(t / top * 100, 2)} for t in range(top, -1, -step)]
    return {"bars": bars, "ticks": ticks, "total": sum(v for _, v in rows)}


@login_required(login_url="login")
def dashboard(request):
    if not request.user.is_staff:
        raise PermissionDenied

    books = Book.objects.all().order_by("-id")
    book_stats = books.aggregate(total=Count("id"), value=Sum("price"), avg=Avg("price"))
    customers = User.objects.filter(is_staff=False).select_related("profile").order_by("-date_joined")

    now = timezone.localtime()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Customers registered per month, last 6 months
    months = []
    cursor = month_start
    for _ in range(6):
        months.append(cursor)
        cursor = (cursor - timedelta(days=1)).replace(day=1)
    months.reverse()

    joined = [timezone.localtime(d) for d in customers.filter(date_joined__gte=months[0]).values_list("date_joined", flat=True)]
    names = MONTH_NAMES.get(request.LANGUAGE_CODE, MONTH_NAMES["en"])
    signup_rows = [
        (names[m.month - 1], sum(1 for d in joined if d.year == m.year and d.month == m.month))
        for m in months
    ]

    # Books by published year (grouped into decades when the spread is wide)
    year_counts = dict(books.values_list("published_year").annotate(c=Count("id")).order_by("published_year"))
    if len(year_counts) > 10:
        decades = {}
        for year, count in year_counts.items():
            decades[year // 10 * 10] = decades.get(year // 10 * 10, 0) + count
        year_rows = [(f"{decade}s", count) for decade, count in sorted(decades.items())]
    else:
        year_rows = [(str(year), count) for year, count in year_counts.items()]

    top_authors = list(books.values("author").annotate(c=Count("id")).order_by("-c", "author")[:5])
    author_peak = max([a["c"] for a in top_authors] + [1])
    for author in top_authors:
        author["pct"] = round(author["c"] / author_peak * 100, 2)

    return render(request, "dashboard.html", {
        "book_stats": book_stats,
        "customer_count": customers.count(),
        "new_customers": customers.filter(date_joined__gte=month_start).count(),
        "signups_chart": build_chart(signup_rows),
        "years_chart": build_chart(year_rows),
        "top_authors": top_authors,
        "no_description": books.filter(Q(description__isnull=True) | Q(description="")).count(),
        "no_image": books.filter(Q(image="") | Q(image__isnull=True)).count(),
        "books": books,
        "customers": customers[:50],
    })
