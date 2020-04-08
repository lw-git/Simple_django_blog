from django.urls import path
from . import views
from .views import (
    BlogListView,
    BlogCreateView,
    BlogUpdateView,
    BlogDeleteView,
)


urlpatterns = [
    path('post/<str:slug>/delete/', BlogDeleteView.as_view(), name='post_delete'),
    path('post/<str:slug>/edit/', BlogUpdateView.as_view(), name='post_edit'),
    path('post/new/', BlogCreateView.as_view(), name='post_new'),
    path('post/<str:slug>/', views.post_detail, name='post_detail'),
    path('posts/by/<str:author>/', BlogListView.as_view(), name='posts_by_author'),
    path('', BlogListView.as_view(), name='home'),
    path('tags/', views.tags_list, name='tag_list'),
    path('tag/<str:slug>/', BlogListView.as_view(), name='tag_detail'),
]
