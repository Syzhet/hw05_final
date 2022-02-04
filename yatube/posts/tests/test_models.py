from django.test import TestCase

from ..models import Post, Group, User

TITLE_FOR_TEST = 'Тестовая группа'
SLUG_FOR_TEST = 'test_slug'
DESCRIPTION_FOR_TEST = 'Тестовое описание'
TEXT_FOR_TEST = 'Тестовый текст'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.USER = User.objects.create_user(username='auth')
        cls.GROUP = Group.objects.create(
            title=TITLE_FOR_TEST,
            slug=SLUG_FOR_TEST,
            description=DESCRIPTION_FOR_TEST,
        )
        cls.POST = Post.objects.create(
            author=cls.USER,
            text=TITLE_FOR_TEST * 10,
        )
        cls.STR_MODELS_VALUES = {
            cls.POST: cls.POST.text[:15],
            cls.GROUP: cls.GROUP.title
        }
        cls.FIELD_VERBOSES = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        cls.FIELD_HELP_TEXTS = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }

    def test_models_have_correct_object_names(self):
        for model, expected_value in self.STR_MODELS_VALUES.items():
            with self.subTest(model=model):
                self.assertEqual(
                    str(model), expected_value)

    def test_verbose_name(self):
        for field, expected_value in self.FIELD_VERBOSES.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.POST._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        for field, expected_value in self.FIELD_HELP_TEXTS.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.POST._meta.get_field(field).help_text, expected_value)
