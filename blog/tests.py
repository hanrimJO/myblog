from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post
from django.utils import timezone
from django.contrib.auth.models import User


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username='smith', password='nopassword')

    def test_post_list(self):
        # /blog/의 상태코드가 200인가?
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

        # 불러온 내용은 맞는가?
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title
        self.assertEqual(title.text, 'Blog')
        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog', navbar.text)
        self.assertIn('AboutMe', navbar.text)

        # 포스트가 없을때
        self.assertEqual(Post.objects.count(), 0)
        self.assertIn('아직 게시물이 없습니다', soup.body.text)

        post_000 = Post.objects.create(
            title='The first Post',
            content='helloworld',
            created=timezone.now(),
            author=self.author_000
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

