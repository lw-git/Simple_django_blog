from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q


from .models import Post, Tag
from .forms import CommentForm


class BlogListView(ListView):

    def get(self, request, author=None):
        search_query = request.GET.get('search', '')

        posts = Post.objects.filter(published=True)

        if search_query:
            posts = Post.objects.filter(Q(title__icontains=search_query) |
                                        Q(body__icontains=search_query),
                                        published=True)

        if author:
            user = get_object_or_404(User, username=author)
            posts = user.posts.filter(published=True)

        paginator = Paginator(posts, 3)
        page_number = request.GET.get('page', 1)
        page = paginator.get_page(page_number)

        is_paginated = page.has_other_pages()

        if page.has_previous():
            prev_url = '?page={}'.format(page.previous_page_number())
        else:
            prev_url = ''

        if page.has_next():
            next_url = '?page={}'.format(page.next_page_number())
        else:
            next_url = ''

        context = {
           'page': page,
           'prev_url': prev_url,
           'next_url': next_url,
           'is_paginated': is_paginated
        }

        return render(request, 'home.html', context)



def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)

    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST, **{'user': request.user})
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post

            if request.user.is_authenticated:
                new_comment.name = request.user.username
                new_comment.email = request.user.email
                if request.user.is_staff:
                    new_comment.author_status = 'staff'
                else:
                    new_comment.author_status = 'user'

            new_comment.save()
            return redirect(reverse('post_detail', args=[slug]))

    else:
        comment_form = CommentForm(**{'user': request.user})

    return render(request, 'post_detail.html',
                  {'post': post,
                   'comments': comments,
                   'comment_form': comment_form,
                   'detail': True})


class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'post_new.html'
    fields = ['title', 'body']
    login_url = 'login'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'post_edit.html'
    fields = ['title', 'body']
    login_url = 'login'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not self.request.user.is_staff:
            if obj.author != self.request.user:
                raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class BlogDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('home')
    login_url = 'login'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not self.request.user.is_staff:
            if obj.author != self.request.user:
                raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


def tags_list(request):
    tags = Tag.objects.all()
    return render(request, 'tag_list.html', {'tags': tags})


def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug__iexact=slug)
    return render(request, 'tag_detail.html', {'tag': tag})
