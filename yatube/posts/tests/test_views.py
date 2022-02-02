from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from ..models import Follow, Post, Group, User


class TaskPagesTests(TestCase):
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

    def test_pages_uses_correct_template(self):
        group = self.GROUP
        post = self.POST
        user = self.USER
        templates_pages_names = {
            reverse('posts:main_page'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{group.slug}'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': f'{user.username}'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{post.pk}'}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
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
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        for i in range(PaginatorTests.SUM_POSTS):
            cls.POST = Post.objects.create(
                text=f'Тестовый текст {i}',
                author=cls.USER,
                group=cls.GROUP,
            )

    def setUp(self):
        self.authorized_test_author = Client()
        self.authorized_test_author.force_login(self.USER)
        group = self.GROUP
        user = self.USER
        self.templates_pages_names = [
            reverse('posts:main_page'),
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{group.slug}'}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': f'{user.username}'}
            ),
        ]

    def test_main_page_correct_context_first_page(self):
        for reverse_name in self.templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_test_author.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    self.POSTS_FOR_FIRST_PAGE
                )

    def test_home_page_correct_context_second_page(self):
        for reverse_name in self.templates_pages_names:
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
        pages_names = [
            reverse('posts:main_page'),
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{self.GROUP.slug}'}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.USER.username}'}
            ),
        ]
        for page in pages_names:
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
        self.first_client = User.objects.create_user(username='client')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.first_client)
        self.second_client = User.objects.create_user(username='client2')
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.second_client)

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
