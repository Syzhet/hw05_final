from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus


class AboutURLtests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.URLS_PAGES = [
            reverse('about:author'),
            reverse('about:tech'),
        ]

    def setUp(self):
        self.guest_client = Client()

    def test_about_urls(self):
        for url in self.URLS_PAGES:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )
