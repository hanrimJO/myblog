from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=25, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, allow_unicode=True) # 한글허용

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'


class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'



class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()

    head_image = models.ImageField(upload_to='blog//%Y/%m/%d', blank=True)

    created = models.DateTimeField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return f'{self.title} :: {self.author}'

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'




