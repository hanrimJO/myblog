from django.urls import path
from basecamp import views

app_name = 'basecamp'

urlpatterns = [
    path('', views.index),
    path('about_me/', views.about_me)
]