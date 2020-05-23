from django.urls import path
from blog import views

app_name = 'blog '


urlpatterns = [
     path('', views.PostList.as_view(), name='index'),
     path('<int:pk>/', views.PostDetail.as_view()),
     path('<int:pk>/update/', views.PostUpdate.as_view()),
     path('category/<str:slug>/', views.PostListByCategory.as_view()),
     path('tag/<str:slug>/', views.PostListByTag.as_view()),
]