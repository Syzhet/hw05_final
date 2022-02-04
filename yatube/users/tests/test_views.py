from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from posts.models import User


class UserPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.USER = User.objects.create_user(username='test_author')
        cls.TEMPLATES_PAGES_NAMES = {
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse(
                'users:password_reset_form'
            ): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
        }
        cls.FORM_FIELDS = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }

    def setUp(self):
        self.authorized_test_author = Client()
        self.authorized_test_author.force_login(self.USER)

    def test_correct_templates(self):
        for reverse_name, template in self.TEMPLATES_PAGES_NAMES.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_test_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_signup(self):
        response = self.authorized_test_author.get(reverse('users:signup'))
        for value, expected in self.FORM_FIELDS.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
