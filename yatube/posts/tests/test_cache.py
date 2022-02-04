from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from ..models import Post, Group, User

TITLE_FOR_TEST = 'Тестовая группа'
SLUG_FOR_TEST = 'test_slug'
DESCRIPTION_FOR_TEST = 'Тестовое описание'
TEXT_FOR_TEST = 'Тестовый текст'


class CacheTests(TestCase):
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

    def setUp(self):
        self.authorized_test_author = Client()
        self.authorized_test_author.force_login(self.USER)

    def test_cache_main_page(self):
        response = self.authorized_test_author.get(
            reverse('posts:main_page')
        )
        context_obj = response.context['page_obj']
        self.assertEqual(context_obj[0].text, 'Тестовый текст')
        content_obj = response.content
        Post.objects.get(id=1).delete()
        response_2 = self.authorized_test_author.get(
            reverse('posts:main_page')
        )
        content_obj_2 = response_2.content
        self.assertEqual(content_obj, content_obj_2)
        cache.clear()
        response_3 = self.authorized_test_author.get(
            reverse('posts:main_page')
        )
        content_obj_3 = response_3.content
        self.assertNotEqual(content_obj, content_obj_3)
