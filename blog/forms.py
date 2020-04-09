from django import forms
from .models import Comment, Post
from pytils.translit import slugify
from django.core.exceptions import ValidationError


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['body'].widget.attrs['placeholder'] = 'Comment text'
        if user.is_authenticated:
            self.fields = {'body': self.fields['body']}


class PostForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance')
        super(PostForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Post
        fields = ['title', 'body', 'tags']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'})
        }

    def clean_title(self):
        new_slug = slugify(self.cleaned_data['title'])

        if new_slug == 'new':
            raise ValidationError('Title may not be "New"')

        count = Post.objects.filter(slug=new_slug).count()

        if self.instance:
            if count and new_slug != self.instance.slug:
                raise ValidationError('Post with that title already exist')
        else:
            if count:
                raise ValidationError('Post with that title already exist')
        return self.cleaned_data['title']
