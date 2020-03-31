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
    path('', BlogListView.as_view(), name='home'),
]
