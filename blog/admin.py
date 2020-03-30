from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title',
    				'author',
    				'slug',
    				'created',
    				'published',
    				'author_status')
    list_filter = ('author', 'published')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'email',
                    'author_status',
                    'post',
                    'created',
                    'active')
    list_filter = ('active', 'author_status', 'created', 'post')
