from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus


class AboutURLtests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls(self):
        urls_pages = [
            reverse('about:author'),
            reverse('about:tech'),
        ]
        for url in urls_pages:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )
