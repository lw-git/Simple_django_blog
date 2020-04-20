import tempfile
from PIL import Image
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


from .models import Post, Tag


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


class TagListTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.tag1 = Tag.objects.create(
            title='tag1'
        )
        self.tag2 = Tag.objects.create(
            title='tag2'
        )
        self.tag3 = Tag.objects.create(
            title='tag3'
        )

    def test_tag_list_status_code(self):
        response = self.client.get(reverse('tag_list'))
        self.assertEqual(response.status_code, 200)

    def test_tag_list_template(self):
        response = self.client.get(reverse('tag_list'))
        self.assertTemplateUsed(response, 'tag_list.html')

    def test_tag_list_content(self):
        response = self.client.get(reverse('tag_list'))
        self.assertContains(response, self.tag1.title)
        self.assertContains(response, self.tag2.title)
        self.assertContains(response, self.tag3.title)
