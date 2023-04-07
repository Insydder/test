from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client, TestCase
from django import forms

from ..models import Post, Group

User = get_user_model()

POSTS_ON_PAGE = 10


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test_slug',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='test2_slug2',
            slug='test2_slug2',
            description='Тестовое2 описание2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.post_2 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group_2
        )
        cls.post_3 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.user = PostPagesTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}
                    ): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}
                    ): 'posts/profile.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}
                    ): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}
                    ): 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_display_post_with_group_on_page(self):
        if PostPagesTests.group.title is not None:
            address = [
                reverse('posts:index'),
                reverse('posts:group_list', kwargs={'slug': self.group.slug}),
                reverse('posts:profile', kwargs={
                    'username': self.user.username}),
            ]
        for url in address:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                objects = response.context['page_obj']
                other_slug_address = [f'/group/{self.group_2.slug}/', ]
                self.assertIn(PostPagesTests.post, objects)
                self.assertNotIn(PostPagesTests.post, other_slug_address)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)

                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """View post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)

                self.assertIsInstance(form_field, expected)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        first_object = response.context['post']
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        self.assertEqual(post_author_0, self.post.author.username)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.post.group)

    def test_index_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_text_0, self.post.text)

    def test_group_list_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.post.group)

    def test_profile_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={
                'username': self.post.author.username}))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_text_0, self.post.text)
        sec_obj = response.context['username']
        self.assertEqual(sec_obj, self.user)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test_slug',
            slug='test_slug',
            description='Тестовое описание',
        )
        Post.objects.bulk_create(
            [
                Post(
                    text=f'Тестовый пост {i}',
                    author=cls.user, group=cls.group
                ) for i in range(POSTS_ON_PAGE + 1)
            ]
        )

    def setUp(self):
        self.user = PaginatorViewsTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginate(self):
        address = {
            'posts:index': {},
            'posts:group_list': {'slug': self.group.slug},
            'posts:profile': {'username': self.user.username},
        }
        for url, kwargs in address.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(reverse(
                    url, kwargs=kwargs))
                self.assertEqual(len(response.context[
                    'page_obj']), POSTS_ON_PAGE)
                response = self.authorized_client.get(reverse(
                    url, kwargs=kwargs) + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 1)
