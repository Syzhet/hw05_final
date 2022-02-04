import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from http import HTTPStatus
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from ..models import Post, Group, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
TITLE_FOR_TEST = 'Тестовая группа'
SLUG_FOR_TEST = 'test_slug'
DESCRIPTION_FOR_TEST = 'Тестовое описание'
TEXT_FOR_TEST = 'Тестовый текст'


class FormsTests(TestCase):
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

    def test_create_form(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст1',
            'group': self.POST.group.id,
        }
        response = self.authorized_test_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.POST.author.username}'}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post1 = Post.objects.get(id=2)
        self.assertEqual(post1.text, 'Тестовый текст1')
        self.assertEqual(post1.author.username, 'test_author')
        self.assertEqual(post1.group.title, 'Тестовая группа')

    def test_edit_post(self):
        self.group1 = Group.objects.create(
            title='Тестовая группа1',
            slug='test_slug1',
            description='Тестовое описание1',
        )
        form_data = {
            'text': 'Тестовый текст изменен',
            'group': self.group1.id,
        }
        response = self.authorized_test_author.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{self.POST.id}'}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.POST.id}'}
            )
        )
        post_object = Post.objects.get(id=self.POST.id)
        self.assertEqual(post_object.text, form_data['text'])
        self.assertEqual(post_object.author.username, 'test_author')
        self.assertEqual(post_object.group.title, 'Тестовая группа1')
        self.assertNotEqual(post_object.group.title, 'Тестовая группа')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTestsPicture(TestCase):
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

    def test_create_form_picture(self):
        small_gif_1 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small1.gif',
            content=small_gif_1,
            content_type='image/gif'
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст1',
            'group': self.POST.group.id,
            'image': uploaded,
        }
        response = self.authorized_test_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.POST.author.username}'}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post1 = Post.objects.get(id=2)
        self.assertEqual(post1.text, 'Тестовый текст1')
        self.assertEqual(post1.author.username, 'test_author')
        self.assertEqual(post1.group.title, 'Тестовая группа')
        self.assertEqual(post1.image, 'posts/small1.gif')


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
        self.guest_user = Client()

    def test_guest_comment(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий1',
        }
        self.guest_user.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': f'{self.POST.pk}'}
            ),
            data=form_data,
            follow=True
        )
        self.assertNotEqual(Comment.objects.count(), comments_count + 1)

    def test_authorizied_comment(self):
        comments_count = Comment.objects.count()
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
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        comment_object = Comment.objects.get(id=1)
        self.assertEqual(comment_object.text, 'Тестовый комментарий')
