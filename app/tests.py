from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .models import Book

User = get_user_model()


def make_test_image(filename="book.png"):
    image = Image.new("RGB", (10, 10), color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return SimpleUploadedFile(filename, buffer.getvalue(), content_type="image/png")


class AuthAndLanguageTests(TestCase):
    def test_login_page_is_accessible(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_user_can_login_and_redirect(self):
        user = User.objects.create_user(username="admin", password="pass123")

        response = self.client.post(
            reverse("login"),
            {"user_id": user.id, "password": "pass123"},
            follow=True,
        )

        self.assertTrue(response.context["user"].is_authenticated)
        self.assertRedirects(response, reverse("book_list"))

    def test_user_can_register_and_login_with_generated_id(self):
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Nodir",
                "last_name": "Sattorov",
                "phone": "+998901234567",
                "address": "Tashkent",
                "password": "StrongPass123!",
            },
            follow=True,
        )

        user = User.objects.get(first_name="Nodir", last_name="Sattorov")
        self.assertEqual(user.username, str(user.id))
        self.assertEqual(user.profile.phone, "+998901234567")
        self.assertEqual(user.profile.address, "Tashkent")
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertRedirects(response, reverse("book_list"))

        login_response = self.client.post(
            reverse("login"),
            {"user_id": user.id, "password": "StrongPass123!"},
            follow=True,
        )
        self.assertTrue(login_response.context["user"].is_authenticated)


class BookAdminAccessTests(TestCase):
    def test_non_admin_cannot_access_book_creation(self):
        user = User.objects.create_user(username="reader", password="pass123")
        self.client.login(username="reader", password="pass123")

        response = self.client.get(reverse("book_create"))

        self.assertEqual(response.status_code, 403)
        self.assertFalse(user.is_staff)


class NavigationAccessTests(TestCase):
    def test_guest_sees_login_and_admin_buttons(self):
        response = self.client.get(reverse("book_list"))
        self.assertContains(response, "Kirish")
        self.assertContains(response, "Ro'yxatdan")
        self.assertContains(response, "Admin")
        self.assertContains(response, "/admin/")

    def test_staff_user_sees_admin_button(self):
        User.objects.create_user(
            username="abduxamid",
            password="abduxamid2013",
            is_staff=True,
            is_superuser=True,
        )
        self.client.login(username="abduxamid", password="abduxamid2013")

        response = self.client.get(reverse("book_list"))
        self.assertContains(response, "Admin")
        self.assertContains(response, "/admin/")


class BookUpdateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="editor", password="pass123")
        self.book = Book.objects.create(
            title="Original title",
            author="Original author",
            price=150000,
            description="Old description",
            published_year=2023,
            image=make_test_image("book.png"),
        )

    def test_book_update_redirects_to_home_page(self):
        self.client.login(username="editor", password="pass123")

        response = self.client.post(
            reverse("book_update", args=[self.book.id]),
            {
                "title": "Updated title",
                "author": "Updated author",
                "price": "200000",
                "description": "New description",
                "published_year": "2025",
                "image": make_test_image("updated-book.png"),
            },
            follow=True,
        )

        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Updated title")
        self.assertRedirects(response, reverse("book_list"))


class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="reader", password="pass123")

    def test_profile_requires_login(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)

    def test_profile_does_not_show_bio_field(self):
        self.client.login(username="reader", password="pass123")

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Bio")
        self.assertNotContains(response, "Biografiya")

    def test_user_can_save_profile_details(self):
        self.client.login(username="reader", password="pass123")

        response = self.client.post(
            reverse("profile"),
            {
                "first_name": "Ali",
                "last_name": "Valiyev",
                "phone": "+998901234567",
                "address": "Tashkent",
            },
            follow=True,
        )

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Ali")
        self.assertEqual(self.user.last_name, "Valiyev")
        self.assertEqual(self.user.profile.phone, "+998901234567")
        self.assertEqual(self.user.profile.address, "Tashkent")
        self.assertRedirects(response, reverse("book_list"))
        self.assertContains(response, "Profile updated")
