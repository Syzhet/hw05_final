import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from http import HTTPStatus
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Post, Group, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class FormsTests(TestCase):
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
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.POST = Post.objects.create(
            text='Тестовый текст',
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

    def test_create_form_picture(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small1.gif',
            content=small_gif,
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
