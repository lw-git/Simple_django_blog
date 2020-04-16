from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q


from .models import Post, Tag
from .forms import CommentForm, PostForm, TagForm


class BlogListView(ListView):
    paginate_by = 3
    template_name = 'home.html'
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = Post.objects.filter(published=True)
        if 'slug' in self.kwargs:
            tag = get_object_or_404(Tag, slug__iexact=self.kwargs['slug'])
            queryset = tag.posts.all()

        if 'search' in self.request.GET:
            queryset = Post.objects.filter(Q(title__icontains=self.request.GET['search']) |
                                        Q(body__icontains=self.request.GET['search']),
                                        published=True)

        if 'author' in self.kwargs:
            user = get_object_or_404(User, username=self.kwargs['author'])
            queryset = user.posts.filter(published=True)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(BlogListView, self).get_context_data(*args, **kwargs)
        context['tag_slug'] = self.kwargs.get('slug')
        context['tag_detail'] = False
        posts = self.get_queryset()
        paginator = Paginator(posts, 3)
        page_number = self.request.GET.get('page', 1)
        context['page'] = paginator.get_page(page_number)
        context['posts_count'] = len(posts)
        if context['tag_slug']:
            context['tag_detail'] = True
        return context


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
    template_name = 'form.html'
    login_url = 'login'
    extra_context = {'object_name': 'Post'}

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'form.html'
    login_url = 'login'
    extra_context = {'update': True, 'object_name': 'Post'}

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not self.request.user.is_staff:
            if obj.author != self.request.user:
                raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class BlogDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'form.html'
    success_url = reverse_lazy('home')
    login_url = 'login'
    extra_context = {'delete': True, 'object_name': 'Post'}

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
    template_name = 'form.html'
    login_url = 'login'
    extra_context = {'object_name': 'Tag'}

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('tag_list')


class TagUpdateView(LoginRequiredMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = 'form.html'
    success_url = reverse_lazy('tag_list')
    login_url = 'login'
    extra_context = {'update': True, 'object_name': 'Tag'}

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class TagDeleteView(LoginRequiredMixin, DeleteView):
    model = Tag
    template_name = 'form.html'
    success_url = reverse_lazy('tag_list')
    login_url = 'login'
    extra_context = {'delete': True, 'object_name': 'Tag'}

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
