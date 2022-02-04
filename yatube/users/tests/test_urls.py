from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

from posts.models import User


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.URLS_PAGES = [
            reverse('users:logout'),
            reverse('users:signup'),
            reverse('users:login'),
            reverse('users:password_reset_form'),
            reverse('users:password_reset_done'),
            reverse('users:password_reset_complete'),
        ]

    def setUp(self):
        self.USER = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.USER)

    def test_urls_users(self):
        for url in self.URLS_PAGES:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )

    def test_change_password(self):
        url = reverse('users:password_change')
        response = self.authorized_client.get(url)
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK
        )

    def test_change_password_done(self):
        url = reverse('users:password_change_done')
        response = self.authorized_client.get(url)
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK
        )
