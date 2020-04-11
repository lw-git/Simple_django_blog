from django.contrib import admin
from .models import Post, Comment, Tag
from django.forms import TextInput, Textarea
from django.db import models
from django.utils.text import Truncator


class CommentInline(admin.TabularInline):
    model = Comment
    exclude = ['email', 'author_status', 'created']
    extra = 1

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '20'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 115})},
    }


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [
        CommentInline,
    ]
    list_display = ('title', 'author', 'created', 'published', 'author_status')
    list_filter = ('author', 'published')
    list_editable = ('published',)


def truncate_field(obj):
    body = "%s" % obj.body
    return Truncator(body).chars(40)


truncate_field.short_description = 'Short text of comment'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post',
                    'name',
                    truncate_field,
                    'active')
    list_filter = ('active', 'post', 'name')
    list_editable = ('active',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
