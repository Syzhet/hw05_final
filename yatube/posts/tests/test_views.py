import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from ..models import Follow, Post, Group, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
TITLE_FOR_TEST = 'Тестовая группа'
SLUG_FOR_TEST = 'test_slug'
DESCRIPTION_FOR_TEST = 'Тестовое описание'
TEXT_FOR_TEST = 'Тестовый текст'


class TaskPagesTests(TestCase):
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
        cls.TEMPLATES_PAGES_NAMES = {
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
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

    def setUp(self):
        self.authorized_test_author = Client()
        self.authorized_test_author.force_login(self.USER)

    def test_pages_uses_correct_template(self):
        for reverse_name, template in self.TEMPLATES_PAGES_NAMES.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_test_author.get(reverse_name)
                self.assertTemplateUsed(response, template)


class PaginatorTests(TestCase):
    POSTS_FOR_FIRST_PAGE = 10
    POSTS_FOR_SECOND_PAGE = 5
    SUM_POSTS = 15

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.USER = User.objects.create_user(username='test1_author')
        cls.GROUP = Group.objects.create(
            title=TITLE_FOR_TEST,
            slug=SLUG_FOR_TEST,
            description=DESCRIPTION_FOR_TEST,
        )
        for i in range(PaginatorTests.SUM_POSTS):
            cls.POST = Post.objects.create(
                text=f'{TEXT_FOR_TEST} {i}',
                author=cls.USER,
                group=cls.GROUP,
            )
        cls.TEMPLATES_PAGES_NAMES = [
            reverse('posts:main_page'),
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{cls.GROUP.slug}'}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': f'{cls.USER.username}'}
            ),
        ]

    def setUp(self):
        self.authorized_test_author = Client()
        self.authorized_test_author.force_login(self.USER)

    def test_main_page_correct_context_first_page(self):
        for reverse_name in self.TEMPLATES_PAGES_NAMES:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_test_author.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    self.POSTS_FOR_FIRST_PAGE
                )

    def test_home_page_correct_context_second_page(self):
        for reverse_name in self.TEMPLATES_PAGES_NAMES:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_test_author.get(
                    reverse_name
                    + '?page=2'
                )
                self.assertEqual(
                    len(response.context['page_obj']),
                    self.POSTS_FOR_SECOND_PAGE
                )


class ContextPagesTests(TestCase):
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
        cls.PAGES_NAMES = [
            reverse('posts:main_page'),
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{cls.GROUP.slug}'}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': f'{cls.USER.username}'}
            ),
        ]

    def setUp(self):
        self.authorized_test_author = Client()
        self.authorized_test_author.force_login(self.USER)
        cache.clear()

    def test_context_index(self):
        response = self.authorized_test_author.get(
            reverse('posts:main_page')
        )
        post_object = response.context['page_obj']
        self.assertEqual(post_object[0].text, 'Тестовый текст')
        self.assertEqual(post_object[0].author.username, 'test_author')
        self.assertEqual(post_object[0].group.title, 'Тестовая группа')

    def test_context_group_list(self):
        response = self.authorized_test_author.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.GROUP.slug}'}
                    )
        )
        group_object = response.context['group']
        self.assertEqual(group_object.title, 'Тестовая группа')
        self.assertEqual(group_object.slug, 'test_slug')
        self.assertEqual(group_object.description, 'Тестовое описание')

    def test_context_profile(self):
        response = self.authorized_test_author.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.USER.username}'}
                    )
        )
        author_object = response.context['author']
        self.assertEqual(author_object.username, 'test_author')

    def test_context_post_detail(self):
        response = self.authorized_test_author.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.POST.pk}'}
                    )
        )
        post_object = response.context['post']
        self.assertEqual(post_object.text, 'Тестовый текст')
        self.assertEqual(post_object.author.username, 'test_author')
        self.assertEqual(post_object.group.title, 'Тестовая группа')

    def test_context_post_create(self):
        response = self.authorized_test_author.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_context_post_edit(self):
        response = self.authorized_test_author.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.POST.pk}'}
                    )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        is_edit_object = response.context['is_edit']
        post_object = response.context['post']
        self.assertTrue(is_edit_object)
        self.assertEqual(post_object.text, 'Тестовый текст')
        self.assertEqual(post_object.author.username, 'test_author')
        self.assertEqual(post_object.group.title, 'Тестовая группа')

    def test_exists_post_in_three_group(self):
        for page in self.PAGES_NAMES:
            with self.subTest(page=page):
                response = self.authorized_test_author.get(page)
                self.assertIn(
                    Post.objects.get(pk=self.POST.pk),
                    response.context['page_obj']
                )


class FollowTests(TestCase):
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
        self.first_client = User.objects.create_user(username='client')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.first_client)
        self.second_client = User.objects.create_user(username='client2')
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.second_client)
        cache.clear()

    def test_follow_and_unfollow(self):
        follow_count_first = Follow.objects.count()
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': f'{self.USER.username}'}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count_first + 1)
        follow_object = Follow.objects.first()
        self.assertEqual(follow_object.user.username, 'client')
        self.assertEqual(follow_object.author.username, 'test_author')
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': f'{self.USER.username}'}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count_first)

    def test_context_follow(self):
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': f'{self.USER.username}'}
            )
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        post_obj = response.context['page_obj']
        self.assertEqual(post_obj[0].text, 'Тестовый текст')
        self.assertEqual(post_obj[0].author, self.USER)
        self.assertEqual(post_obj[0].group, self.GROUP)
        response_2 = self.authorized_client_2.get(
            reverse('posts:follow_index')
        )
        post_obj_2 = response_2.context['page_obj']
        self.assertFalse(post_obj_2)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ContextTestsPicture(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
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
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_test_author = Client()
        self.authorized_test_author.force_login(self.USER)
        cache.clear()

    def test_main_page_context_picture(self):
        response = self.authorized_test_author.get(
            reverse('posts:main_page')
        )
        post_object = response.context['page_obj']
        self.assertEqual(post_object[0].image, 'posts/small.gif')

    def test_context_group_list(self):
        response = self.authorized_test_author.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.GROUP.slug}'}
                    )
        )
        group_object = response.context['page_obj']
        self.assertEqual(group_object[0].image, 'posts/small.gif')

    def test_profile_context_picture(self):
        response = self.authorized_test_author.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.USER.username}'}
                    )
        )
        post_object = response.context['page_obj']
        self.assertEqual(post_object[0].image, 'posts/small.gif')
        author_object = response.context['author']
        self.assertEqual(author_object.username, 'test_author')

    def test_context_post_detail(self):
        response = self.authorized_test_author.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.POST.pk}'}
                    )
        )
        post_object = response.context['post']
        self.assertEqual(post_object.image, 'posts/small.gif')


class CommentTests(TestCase):
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

    def test_context_post_detail_comment(self):
        form_data = {
            'text': 'Тестовый комментарий',
        }
        self.authorized_test_author.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': f'{self.POST.pk}'}
            ),
            data=form_data,
            follow=True
        )
        response = self.authorized_test_author.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.POST.pk}'}
                    )
        )
        comment_object = response.context['comments']
        self.assertEqual(comment_object[0].text, 'Тестовый комментарий')
