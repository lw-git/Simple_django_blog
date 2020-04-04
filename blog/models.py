from django.db import models
from django.urls import reverse
from pytils.translit import slugify


class Post(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='posts'
    )

    body = models.TextField()
    slug = models.SlugField(max_length=250, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=True)
    author_status = models.CharField(max_length=30, default='user')
    photo = models.ImageField(upload_to='photos/', blank=True)
    tags = models.ManyToManyField('Tag', blank=True, related_name='posts')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        if self.author.is_staff:
            self.author_status = 'staff'

        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.slug)])

    class Meta:
        ordering = ('-created',)


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='comments',
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField(max_length=2000)
    created = models.DateTimeField(auto_now_add=True)
    # anonymous, user, staff
    author_status = models.CharField(max_length=30, default='anonymous')
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.post)


class Tag(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(default='slug', max_length=100, unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Tag, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('tag_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
