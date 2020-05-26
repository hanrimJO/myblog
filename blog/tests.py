from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category, Tag, Comment
from django.utils import timezone
from django.contrib.auth.models import User


def create_category(name='Life', description=''):
    category, is_created = Category.objects.get_or_create(
        name=name,
        description=description
    )

    category.slug = category.name.replace(' ', '-').replace('/', '')
    category.save()

    return category


def create_tag(name='django'):
    tag, is_created = Tag.objects.get_or_create(
        name=name
    )
    tag.slug = tag.name.replace(' ', '-').replace('/', '')
    tag.save()

    return tag


def create_comment(post, text='some comments', author=None):
    if author is None:
        author, is_created = User.objects.get_or_create(
            username='guest',
            password='guestpassword'
        )
    comment = Comment.objects.create(
        post=post,
        text=text,
        author=author
    )
    return comment


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

    def test_tag(self):
        tag_000 = create_tag(name='django')
        tag_001 = create_tag(name='til')
        post_000 = create_post(
            title='the first post',
            content='Hello world',
            author=self.author_000,
        )
        post_001 = create_post(
            title='d is silence',
            content='django unchained',
            author=self.author_000,
        )
        post_000.tags.add(tag_000)
        post_000.tags.add(tag_001)
        post_000.save()
        post_001.tags.add(tag_001)
        post_001.save()

        self.assertEqual(post_000.tags.count(), 2)
        self.assertEqual(tag_001.post_set.count(), 2)
        self.assertEqual(tag_001.post_set.first(), post_000)
        self.assertEqual(tag_001.post_set.last(), post_001)

    def test_post(self):
        category = create_category()
        post_000 = create_post(
            title='the first post',
            content='Hello world',
            author=self.author_000,
            category=category
        )

    def test_comment(self):
        post_000 = create_post(
            title='the first post',
            content='Hello world',
            author=self.author_000,
        )
        self.assertEqual(Comment.objects.count(), 0)
        comment_000 = create_comment(
            post=post_000,
            text='first_comment',
        )
        comment_001 = create_comment(
            post=post_000,
            text='second comment'
        )
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(post_000.comment_set.count(), 2)


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create_user(username='smith', password='nopassword')
        self.author_trump = User.objects.create_user(username='trump', password='nopassword')

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
        tag_django = create_tag(name='django')
        post_000 = create_post(
            title='the first post',
            content='Hello world',
            author=self.author_000,
        )
        post_000.tags.add(tag_django)
        post_000.save()
        post_001 = create_post(
            title='d is silence',
            content='django unchanined',
            author=self.author_000,
            category=create_category(name='Django')
        )
        post_001.tags.add(tag_django)
        post_001.save()

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
        main_div = soup.find('div', id='main-div')
        self.assertIn('Django', main_div.text)
        self.assertIn('기타', main_div.text)

        # Tag test
        post_card_000 = main_div.find('div', id=f'post-card-{post_000.pk}')

        self.assertIn('#django', post_card_000.text)


    def test_post_detail(self):
        category_django = create_category(name='Django')
        post_000 = create_post(
            title='the first post',
            content='Hello world',
            author=self.author_000,
            category=category_django
        )
        comment_000 = create_comment(post_000, text='test comment', author=self.author_trump)
        comment_001 = create_comment(post_000, text='test comment', author=self.author_000)

        tag_django = create_tag(name='django')
        post_000.tags.add(tag_django)
        post_000.save()

        post_001 = create_post(
            title='d is silence',
            content='django unchanined',
            author=self.author_000,
        )

        self.assertGreater(Post.objects.count(), 0)
        post_000_url = post_000.get_absolute_url()
        self.assertEqual(post_000_url, f'/blog/{post_000.pk}/')

        response = self.client.get(post_000_url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title
        self.assertEqual(title.text, f'{post_000.title} - Blog')

        self.check_navbar(soup)

        body = soup.body
        main_div = body.find('div', id='main-div')
        self.assertIn(post_000.title, main_div.text)
        self.assertIn(post_000.author.username, main_div.text)
        self.assertIn(post_000.content, main_div.text)

        #카테고리
        self.check_right_side(soup)

        # Comment
        comment_div = main_div.find('div', id='comment-list')
        self.assertIn(comment_000.author.username, comment_div.text)
        self.assertIn(comment_000.text, comment_div.text)


        # Tag test

        self.assertIn('#django', main_div.text)

        self.assertIn(category_django.name, main_div.text)
        self.assertNotIn('EDIT', main_div.text)

        # login
        login_success = self.client.login(username='smith', password='nopassword')
        response = self.client.get(post_000_url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')
        self.assertTrue(login_success)
        self.assertEqual(post_000.author, self.author_000)
        self.assertIn('EDIT', main_div.text)

        # not author login
        login_success = self.client.login(username='trump', password='nopassword')
        response = self.client.get(post_000_url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')
        self.assertTrue(login_success)
        self.assertEqual(post_000.author, self.author_000)
        self.assertNotIn('EDIT', main_div.text)

        comment_div = main_div.find('div', id=f'comment-list')
        comment_000_div = comment_div.find('div', id=f'comment-id-{comment_000.pk}')
        self.assertIn('edit', comment_000_div.text)
        self.assertIn('delete', comment_000_div.text)

        comment_001_div = comment_div.find('div', id=f'comment-id-{comment_001.pk}')
        self.assertNotIn('edit', comment_001_div.text)
        self.assertNotIn('delete', comment_001_div.text)



    def test_post_list_by_category(self):
        category_django = create_category(name='Django')
        post_000 = create_post(
            title='the first post',
            content='Hello world',
            author=self.author_000,
        )
        post_001 = create_post(
            title='d is silence',
            content='django unchanined',
            author=self.author_000,
            category=category_django
        )

        response = self.client.get(category_django.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # self.assertEqual(f'Blog - {category_django.name}', soup.title.text)
        main_div = soup.find('div', id='main-div')
        self.assertNotIn('기타', main_div.text)
        self.assertIn(category_django.name, main_div.text)

    def test_post_list_no_category(self):
        category_django = create_category(name='Django')
        post_000 = create_post(
            title='the first post',
            content='Hello world',
            author=self.author_000,
        )
        post_001 = create_post(
            title='d is silence',
            content='django unchanined',
            author=self.author_000,
            category=category_django
        )

        response = self.client.get('/blog/category/_none/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        main_div = soup.find('div', id='main-div')
        self.assertIn('기타', main_div.text)
        self.assertNotIn(category_django.name, main_div.text)

    def test_tag_page(self):
        tag_000 = create_tag(name='django')
        tag_001 = create_tag(name='til')
        post_000 = create_post(
            title='the first post',
            content='Hello world',
            author=self.author_000,
        )
        post_001 = create_post(
            title='d is silence',
            content='django unchained',
            author=self.author_000,
        )
        post_000.tags.add(tag_000)
        post_000.tags.add(tag_001)
        post_000.save()
        post_001.tags.add(tag_001)
        post_001.save()

        response = self.client.get(tag_000.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')

        self.assertIn(f'#{tag_000.name}', main_div.text)
        self.assertIn(post_000.title, main_div.text)
        self.assertNotIn(post_001.title, main_div.text)

    def test_post_create(self):
        response = self.client.get('/blog/create/')
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username='smith', password='nopassword')
        response = self.client.get('/blog/create/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main_div')

    def test_post_update(self):
        post_000 = create_post(
            title='The first post',
            content='Hello World, weare the world',
            author=self.author_000,
        )
        self.assertEqual(post_000.get_update_url(), post_000.get_absolute_url() + 'update/')
        response = self.client.get(post_000.get_update_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        main_div = soup.find('div', id='main-div')
        self.assertNotIn('Created', main_div.text)
        self.assertNotIn('Author', main_div.text)

    def test_new_comment(self):
        post_000 = create_post(
            title='The first post',
            content='Hello World, weare the world',
            author=self.author_000,
        )
        login_success = self.client.login(username='smith', password='nopassword')
        self.assertTrue(login_success)
        response = self.client.post(
            post_000.get_absolute_url()+'new_comment/',
            {'text': 'A test comment for the first post'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')
        self.assertIn(post_000.title, main_div.text)
        self.assertIn('A test comment', main_div.text)

