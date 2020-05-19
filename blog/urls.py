from django.urls import path
from blog import views

app_name = 'blog '


urlpatterns = [
     path('', views.PostList.as_view(), name='index'),
     path('<int:pk>', views.PostDetail.as_view())
]