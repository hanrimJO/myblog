from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category
from django.utils import timezone
from django.contrib.auth.models import User


def create_category(name='Life', description=''):
    category, is_created = Category.objects.get_or_create(
        name=name,
        description=description
    )

    return category


def create_post(title, content, author, category=None):
    post_000 = Post.objects.create(
        title=title,
        content=content,
        created=timezone.now(),
        author=author,
        category=category
    )
    return post_000


class TestModel(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username='smith', password='nopassword')

    def test_category(self):
        category = create_category()

        post_000 = create_post(
            title='the first post',
            content='Hello world',
            author=self.author_000,
            category=category
        )
        self.assertEqual(category.post_set.count(), 1)

    def test_post(self):
        category = create_category()
        post_000 = create_post(
            title='the first post',
            content='Hello world',
            author=self.author_000,
            category=category
        )


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username='smith', password='nopassword')

    def check_navbar(self, soup):
        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog', navbar.text)
        self.assertIn('AboutMe', navbar.text)

    def check_right_side(self, soup):
        category_card = soup.find('div', id='category-card')
        self.assertIn('기타 (1)', category_card.text)
        self.assertIn('Django (1)', category_card.text)

    def test_post_list_no_post(self):
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

    def test_post_list_post(self):
        post_000 = create_post(
            title='the first post',
            content='Hello world',
            author=self.author_000,
        )
        post_001 = create_post(
            title='d is silence',
            content='django unchanined',
            author=self.author_000,
            category=create_category(name='Django')
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

        # readmore 클릭시
        post_000_read_more_btn = body.find('a', id=f'read-more-post-{post_000.pk}')
        self.assertEqual(post_000_read_more_btn['href'], post_000.get_absolute_url())

        self.check_right_side(soup)
        # 카테고리
        main_div = soup.find('div', id='main_div')
        self.assertIn('Django', main_div.text)
        self.assertIn('기타', main_div.text)

    def test_post_detail(self):
        post_000 = create_post(
            title='the first post',
            content='Hello world',
            author=self.author_000,
        )
        post_001 = create_post(
            title='d is silence',
            content='django unchanined',
            author=self.author_000,
            category=create_category(name='Django')
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

        body = soup.body
        main_div = body.find('div', id='main_div')
        self.assertIn(post_000.title, main_div.text)
        self.assertIn(post_000.author.username, main_div.text)
        self.assertIn(post_000.content, main_div.text)

        #카테고리
        self.check_right_side(soup)
