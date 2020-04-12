from django.urls import path
from . import views


urlpatterns = [
    path('post/<str:slug>/delete/', views.BlogDeleteView.as_view(), name='post_delete'),
    path('post/<str:slug>/edit/', views.BlogUpdateView.as_view(), name='post_edit'),
    path('post/new/', views.BlogCreateView.as_view(), name='post_new'),
    path('post/<str:slug>/', views.BlogDetailView.as_view(), name='post_detail'),
    path('posts/by/<str:author>/', views.BlogListView.as_view(), name='posts_by_author'),
    path('', views.BlogListView.as_view(), name='home'),
    path('tag/<str:slug>/delete/', views.TagDeleteView.as_view(), name='tag_delete'),
    path('tag/<str:slug>/edit/', views.TagUpdateView.as_view(), name='tag_edit'),
    path('tag/new/', views.TagCreateView.as_view(), name='tag_new'),
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tag/<str:slug>/', views.BlogListView.as_view(), name='tag_detail'),
]
