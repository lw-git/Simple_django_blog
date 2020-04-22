import tempfile
from PIL import Image
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase


from blog.models import Post, Tag, Comment


class PostModelTests(TestCase):

    def setUp(self):
        self.tag1 = Tag.objects.create(
            title='Super Tag'
        )
        self.tag2 = Tag.objects.create(
            title='Another Tag'
        )

        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )

        self.superuser = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@email.com',
            password='supersecret'
        )
        self.post = Post.objects.create(
            title='New Post',
            body='New content',
            author=self.user
        )
        self.post.tags.set([self.tag1, self.tag2])

        self.admin_post = Post.objects.create(
            title='Post 2',
            body='Content of post 2',
            author=self.superuser
        )

    def test_string_representation(self):
        self.assertEqual(str(self.post), self.post.title)

    def test_slug(self):
        self.assertEqual(self.post.slug, 'new-post')

    def test_get_absolute_url(self):
        self.assertEqual(self.post.get_absolute_url(), '/post/' + self.post.slug + '/')

    def test_tags(self):
        self.assertEqual(self.post.tags.all().count(), 2)
        self.assertEqual(self.post.tags.get(id=self.tag1.id), self.tag1)
        self.assertEqual(self.post.tags.get(id=self.tag2.id), self.tag2)

    def test_author_status(self):
        self.assertEqual(self.post.author_status, 'user')
        self.assertEqual(self.admin_post.author_status, 'staff')

    def test_photo_url(self):
        with tempfile.NamedTemporaryFile() as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='png')
            ntf.seek(0)

            post_with_image = Post.objects.create(
                title='Post with image',
                body='New image',
                author=self.user,
                photo=ntf.name.split('\\')[-1]
            )
            self.assertEqual(post_with_image.photo.url, settings.MEDIA_URL + ntf.name.split('\\')[-1])

    def test_published(self):
        self.assertTrue(self.post.published)


class CommentModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )

        self.superuser = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@email.com',
            password='supersecret'
        )

        self.post = Post.objects.create(
            title='New Post',
            body='New content',
            author=self.user
        )

        self.comment_from_user = Comment.objects.create(
            post=self.post,
            name=self.user.username,
            email=self.user.email,
            body='Comment from user',
            author_status='user',
        )

        self.comment_from_superuser = Comment.objects.create(
            post=self.post,
            name=self.superuser.username,
            email=self.superuser.email,
            body='Comment from user',
            author_status='staff'
        )

    def test_string_representation(self):
        comment = self.comment_from_user
        self.assertEqual(
            str(comment),
            f'Comment by {comment.name} on {comment.post}'
        )

    def test_comment_is_active(self):
        comment = self.comment_from_user
        self.assertTrue(comment.active)

    def test_author_status(self):
        comment1 = self.comment_from_user
        comment2 = self.comment_from_superuser
        comment3 = Comment.objects.create(
            post=self.post,
            name='Test',
            email='test@test.com',
            body='Some text'
        )
        self.assertEqual(comment1.author_status, 'user')
        self.assertEqual(comment2.author_status, 'staff')
        self.assertEqual(comment3.author_status, 'anonymous')

    def test_other_fields(self):
        comment = self.comment_from_user
        self.assertEqual(comment.name, self.user.username)
        self.assertEqual(comment.email, self.user.email)
        self.assertEqual(comment.body, 'Comment from user')


class TagModelTests(TestCase):

    def setUp(self):
        self.tag = Tag.objects.create(
            title='Super Tag'
        )

    def test_string_representation(self):
        self.assertEqual(str(self.tag), self.tag.title)

    def test_slug(self):
        self.assertEqual(self.tag.slug, 'super-tag')

    def test_get_absolute_url(self):
        self.assertEqual(self.tag.get_absolute_url(), '/tag/' + self.tag.slug + '/')
