from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author')
    list_filter = ('author',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'email',
                    'author_status',
                    'post',
                    'created',
                    'active')
    list_filter = ('active', 'author_status', 'created', 'post')
