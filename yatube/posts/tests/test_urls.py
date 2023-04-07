from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostsURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_public_urls(self):
        address_status_code = {
            '/': 200,
            f'/group/{self.group.slug}/': 200,
            f'/profile/{self.user}/': 200,
            f'/posts/{self.post.id}/': 200,
            '/unexisting_page/': 404
        }
        for address, status_code in address_status_code.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_auth_urls(self):
        address_status_code = {
            '/': 200,
            f'/group/{self.group.slug}/': 200,
            f'/profile/{self.user}/': 200,
            f'/posts/{self.post.id}/': 200,
            '/unexisting_page/': 404,
            '/create/': 200
        }
        for address, status_code in address_status_code.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_redirect_for_guest_user(self):
        post = PostsURLTests.post
        redirect_from = [
            f'/posts/{post.id}/edit/',
            '/create/'
        ]
        for url in redirect_from:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, (f'/auth/login/?next={url}'))

    def test_edit_post_by_author(self):
        post = PostsURLTests.post
        response = self.authorized_client.get(f'/posts/{post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
