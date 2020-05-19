from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post
from django.utils import timezone
from django.contrib.auth.models import User


def create_post(title, content, author):
    post_000 = Post.objects.create(
        title=title,
        content=content,
        created=timezone.now(),
        author=author
    )
    return post_000


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username='smith', password='nopassword')

    def check_navbar(self, soup):
        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog', navbar.text)
        self.assertIn('AboutMe', navbar.text)


    def test_post_list(self):
        # /blog/의 상태코드가 200인가?
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

        # 불러온 내용은 맞는가?
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title
        self.assertEqual(title.text, 'Blog')

        self.check_navbar(soup)

        # 포스트가 없을때
        self.assertEqual(Post.objects.count(), 0)
        self.assertIn('아직 게시물이 없습니다', soup.body.text)

        post_000 = create_post(
            title='the first post',
            content='Hello world',
            author=self.author_000,
        )

        self.assertGreater(Post.objects.count(), 0)
        # 새로고침
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

        # 불러온 내용은 맞는가?
        soup = BeautifulSoup(response.content, 'html.parser')
        body = soup.body

        self.assertNotIn('아직 게시물이 없습니다', body.text)
        self.assertIn(post_000.title, body.text)

    def test_post_detail(self):
        post_000 = create_post(
            title='the first post',
            content='Hello world',
            author=self.author_000,
        )

        self.assertGreater(Post.objects.count(), 0)
        post_000_url = post_000.get_absolute_url()
        self.assertEqual(post_000_url, f'/blog/{post_000.pk}')

        response = self.client.get(post_000_url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title
        self.assertEqual(title.text, f'{post_000.title} - Blog')

        self.check_navbar(soup)

