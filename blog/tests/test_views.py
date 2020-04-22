from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from pytils.translit import slugify


from blog.models import Tag, Post


class TagListViewTests(TestCase):
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


class PostCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()

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
        self.tag1 = Tag.objects.create(
            title='tag1'
        )
        self.tag2 = Tag.objects.create(
            title='tag2'
        )
        self.testpost = Post.objects.create(
            title='New Post',
            body='New content',
            author=self.user
        )

    def test_get_response_for_login_user(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('post_new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'form.html')

    def test_get_response_for_anonymous_user(self):
        response = self.client.get(reverse('post_new'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login') + '?next=/post/new/')

    def test_create_post_for_user(self):
        data = {'title': 'New post from user',
                'body': 'Some text...',
                'tags': [self.tag1.id, self.tag2.id]}

        self.client.login(username='testuser', password='secret')
        response = self.client.post(reverse('post_new'), data)
        self.assertEqual(response.status_code, 302)

        new_post = Post.objects.filter(title__contains='New post from user').first()

        self.assertEqual(new_post.title, 'New post from user')
        self.assertEqual(new_post.body, 'Some text...')
        self.assertEqual(new_post.tags.count(), 2)
        self.assertEqual(new_post.tags.get(id=self.tag1.id), self.tag1)
        self.assertEqual(new_post.tags.get(id=self.tag2.id), self.tag2)
        self.assertEqual(new_post.slug, slugify('New post from user'))
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(new_post.author_status, 'user')

    def test_create_post_for_superuser(self):
        data = {'title': 'New post from superuser',
                'body': 'Some other text...',
                'tags': [self.tag1.id]}

        self.client.login(username='admin', password='supersecret')
        response = self.client.post(reverse('post_new'), data)
        self.assertEqual(response.status_code, 302)

        new_post = Post.objects.filter(title__contains='New post from superuser').first()

        self.assertEqual(new_post.title, 'New post from superuser')
        self.assertEqual(new_post.body, 'Some other text...')
        self.assertEqual(new_post.tags.count(), 1)
        self.assertEqual(new_post.tags.get(id=self.tag1.id), self.tag1)
        self.assertEqual(new_post.slug, slugify('New post from superuser'))
        self.assertEqual(new_post.author, self.superuser)
        self.assertEqual(new_post.author_status, 'staff')

    def test_create_post_with_same_title_fails(self):
        data = {'title': 'New post',
                'body': 'Some text...',
                'tags': [self.tag1.id, self.tag2.id]}

        self.client.login(username='testuser', password='secret')
        response = self.client.post(reverse('post_new'), data)
        self.assertEqual(response.status_code, 302)

    def test_create_post_without_required_field_fails(self):
        data = {'body': 'Some text...'}
        self.client.login(username='testuser', password='secret')
        response = self.client.post(reverse('post_new'), data)
        self.assertEqual(response.status_code, 302)
