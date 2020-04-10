from django.urls import path
from .views import (
    BlogListView,
    TagListView,
    BlogDetailView,
    BlogCreateView,
    BlogUpdateView,
    BlogDeleteView,
)


urlpatterns = [
    path('post/<str:slug>/delete/', BlogDeleteView.as_view(), name='post_delete'),
    path('post/<str:slug>/edit/', BlogUpdateView.as_view(), name='post_edit'),
    path('post/new/', BlogCreateView.as_view(), name='post_new'),
    path('post/<str:slug>/', BlogDetailView.as_view(), name='post_detail'),
    path('posts/by/<str:author>/', BlogListView.as_view(), name='posts_by_author'),
    path('', BlogListView.as_view(), name='home'),
    path('tags/', TagListView.as_view(), name='tag_list'),
    path('tag/<str:slug>/', BlogListView.as_view(), name='tag_detail'),
]
