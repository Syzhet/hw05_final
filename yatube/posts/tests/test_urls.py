from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Post, Group, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.USER = User.objects.create_user(username='test_author')
        cls.GROUP = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.POST = Post.objects.create(
            text='Тестовый текст',
            author=cls.USER,
            group=cls.GROUP,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_test_author = Client()
        self.authorized_test_author.force_login(self.USER)
        self.autorized_user = User.objects.create_user(
            username='NoName'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(
            self.autorized_user
        )

    def test_url_for_guest(self):
        group = self.GROUP
        post = self.POST
        user = self.USER
        urls_pages = [
            '/',
            f'/group/{group.slug}/',
            f'/profile/{user.username}/',
            f'/posts/{post.pk}/',
        ]
        for url in urls_pages:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.OK)
        response1 = self.guest_client.get('/create/')
        self.assertRedirects(
            response1,
            '/auth/login/?next=/create/'
        )
        response1 = self.guest_client.get(f'/posts/{post.pk}/edit/')
        self.assertRedirects(
            response1,
            '/auth/login/?next=/posts/1/edit/'
        )

    def test_for_autorizied(self):
        post = self.POST
        response = self.authorized_client.get('/create/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK
        )
        response1 = self.guest_client.get(f'/posts/{post.pk}/edit/')
        self.assertRedirects(
            response1,
            '/auth/login/?next=/posts/1/edit/'
        )

    def test_for_author(self):
        post = self.POST
        response = self.authorized_test_author.get(f'/posts/{post.pk}/edit/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK
        )

    def test_no_exist_page(self):
        url = '/noexisturl/'
        response = self.guest_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_tempates(self):
        group = self.GROUP
        post = self.POST
        user = self.USER
        templates_collection = {
            '/': 'posts/index.html',
            f'/group/{group.slug}/': 'posts/group_list.html',
            f'/profile/{user.username}/': 'posts/profile.html',
            f'/posts/{post.pk}/': 'posts/post_detail.html',
            f'/posts/{post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_collection.items():
            with self.subTest(address=address):
                response = self.authorized_test_author.get(address)
                self.assertTemplateUsed(response, template)
