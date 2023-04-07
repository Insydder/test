from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

SYMBHOL_LIM = 15
User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        expected_objects = {
            str(post): post.text[:SYMBHOL_LIM],
            str(group): group.title
        }
        for field, expected_object in expected_objects.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_object,
                                 '__str__ не правильно отображает '
                                 'значения в объектах моделей')
