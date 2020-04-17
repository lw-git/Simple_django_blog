from django.urls import path
from . import views


urlpatterns = [
    path('post/<str:slug>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('post/<str:slug>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('post/new/', views.PostCreateView.as_view(), name='post_new'),
    path('post/<str:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/by/<str:author>/', views.PostListView.as_view(), name='posts_by_author'),
    path('', views.PostListView.as_view(), name='home'),
    path('tag/<str:slug>/delete/', views.TagView.as_view(), name='tag_delete'),
    path('tag/<str:slug>/edit/', views.TagView.as_view(), name='tag_edit'),
    path('tag/new/', views.TagView.as_view(), name='tag_new'),
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tag/<str:slug>/', views.PostListView.as_view(), name='tag_detail'),
]
