from django.test import TestCase, Client
from http import HTTPStatus


class TemplateTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_404_template(self):
        response = self.guest_client.get('/noexisturl/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
