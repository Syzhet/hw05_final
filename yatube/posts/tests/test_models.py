from django.test import TestCase


from ..models import Post, Group, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.USER = User.objects.create_user(username='auth')
        cls.GROUP = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.POST = Post.objects.create(
            author=cls.USER,
            text='Тестовая группа' * 10,
        )

    def test_models_have_correct_object_names(self):
        post = self.POST
        group = self.GROUP

        str_models_values = {
            post: post.text[:15],
            group: group.title
        }

        for model, expected_value in str_models_values.items():
            with self.subTest(model=model):
                self.assertEqual(
                    str(model), expected_value)

    def test_verbose_name(self):
        post = self.POST
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        post = self.POST
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
