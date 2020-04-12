from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q


from .models import Post, Tag
from .forms import CommentForm, PostForm, TagForm


class BlogListView(ListView):

    def get(self, request, author=None, slug=None):
        tag_detail = False
        tag_slug = slug
        search_query = request.GET.get('search', '')

        posts = Post.objects.filter(published=True)
        posts_count = posts.count()

        if slug:
            tag = get_object_or_404(Tag, slug__iexact=slug)
            posts = tag.posts.all()
            tag_detail = True

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

        context = {'page': page,
                   'prev_url': prev_url,
                   'next_url': next_url,
                   'is_paginated': is_paginated,
                   'posts_count': posts_count,
                   'tag_detail': tag_detail,
                   'tag_slug': tag_slug}

        return render(request, 'home.html', context)


class BlogDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'post_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(BlogDetailView, self).get_context_data(*args, **kwargs)
        context['comment_form'] = CommentForm(**{'user': self.request.user})
        context['comments'] = self.get_object().comments.filter(active=True)
        context['detail'] = True
        return context

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        form = CommentForm(data=request.POST, **{'user': request.user})
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            user = self.request.user

            if user.is_authenticated:
                new_comment.name = user.username
                new_comment.email = user.email
                if user.is_staff:
                    new_comment.author_status = 'staff'
                else:
                    new_comment.author_status = 'user'

            new_comment.save()
            return redirect(reverse('post_detail', args=[post.slug]))
        else:
            return render(request, 'post_detail.html',
                          {'post': post,
                           'comments': post.comments.filter(active=True),
                           'comment_form': form,
                           'detail': True})


class BlogCreateView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = 'post_new.html'
    login_url = 'login'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
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


class TagListView(ListView):
    model = Tag
    template_name = 'tag_list.html'
    context_object_name = 'tags'

    def get_context_data(self, *args, **kwargs):
        context = super(TagListView, self).get_context_data(*args, **kwargs)
        context['tag_list'] = True
        return context


class TagCreateView(LoginRequiredMixin, CreateView):
    form_class = TagForm
    template_name = 'tag_new.html'
    login_url = 'login'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('tag_list')


class TagUpdateView(LoginRequiredMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = 'tag_edit.html'
    success_url = reverse_lazy('tag_list')
    login_url = 'login'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class TagDeleteView(LoginRequiredMixin, DeleteView):
    model = Tag
    template_name = 'tag_delete.html'
    success_url = reverse_lazy('tag_list')
    login_url = 'login'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
