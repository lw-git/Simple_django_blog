from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse


from .models import Post, Tag
from .forms import CommentForm


class BlogListView(ListView):
    queryset = Post.objects.filter(published=True)
    context_object_name = 'posts'
    template_name = 'home.html'


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
                   'comment_form': comment_form})


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
