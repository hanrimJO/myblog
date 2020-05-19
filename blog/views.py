from django.shortcuts import render, get_object_or_404
from blog.models import Post
from django.views.generic import ListView, DetailView
# Create your views here.


class PostList(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.order_by('-created')


class PostDetail(DetailView):
    model = Post
