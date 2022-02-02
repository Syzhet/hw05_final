from django.test import TestCase, Client
from django.urls import reverse

from posts.models import User


class FormsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_user_create_form(self):
        user_count = User.objects.count()
        form_data = {
            'first_name': 'Юзер',
            'second_name': 'Тестовый',
            'username': 'TestUser',
            'email': 'test@django.ru',
            'password1': 'abasfasa13245',
            'password2': 'abasfasa13245',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertRedirects(
            response,
            reverse('posts:main_page')
        )
