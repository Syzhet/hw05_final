from django.urls import reverse
from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Post, Group, User

TITLE_FOR_TEST = 'Тестовая группа'
SLUG_FOR_TEST = 'test_slug'
DESCRIPTION_FOR_TEST = 'Тестовое описание'
TEXT_FOR_TEST = 'Тестовый текст'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.USER = User.objects.create_user(username='test_author')
        cls.GROUP = Group.objects.create(
            title=TITLE_FOR_TEST,
            slug=SLUG_FOR_TEST,
            description=DESCRIPTION_FOR_TEST,
        )
        cls.POST = Post.objects.create(
            text=TEXT_FOR_TEST,
            author=cls.USER,
            group=cls.GROUP,
        )
        cls.KWARGS_FOR_EDIT = {'post_id': f'{cls.POST.pk}'}
        cls.REVERSE_STRING_FOR_EDIT = (
            f"{reverse('users:login')}?next="
            + f"{reverse('posts:post_edit', kwargs=cls.KWARGS_FOR_EDIT)}"
        )
        cls.URLS_PAGES = [
            reverse('posts:main_page'),
            reverse('posts:group_list', kwargs={'slug': f'{cls.GROUP.slug}'}),
            reverse(
                'posts:profile',
                kwargs={'username': f'{cls.USER.username}'}
            ),
            reverse('posts:post_detail', kwargs={'post_id': f'{cls.POST.pk}'}),
        ]
        cls.TEMPLATES_COLLECTION = {
            reverse('posts:main_page'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{cls.GROUP.slug}'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': f'{cls.USER.username}'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{cls.POST.pk}'}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_create',
            ): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{cls.POST.pk}'}
            ): 'posts/create_post.html',
        }

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
        for url in self.URLS_PAGES:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.OK)
        response1 = self.guest_client.get('/create/')
        self.assertRedirects(
            response1,
            f"{reverse('users:login')}?next={reverse('posts:post_create')}"
        )
        response1 = self.guest_client.get(f'/posts/{self.POST.pk}/edit/')
        self.assertRedirects(
            response1,
            self.REVERSE_STRING_FOR_EDIT
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
            self.REVERSE_STRING_FOR_EDIT
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
        for address, template in self.TEMPLATES_COLLECTION.items():
            with self.subTest(address=address):
                response = self.authorized_test_author.get(address)
                self.assertTemplateUsed(response, template)
