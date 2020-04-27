import time
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


class PostCreateViewTests(TestCase):
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
        self.assertEqual(Post.objects.count(), 1)
        response = self.client.post(reverse('post_new'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), 1)


    def test_create_post_without_required_field_fails(self):
        data = {'body': 'Some text...'}
        self.client.login(username='testuser', password='secret')
        self.assertEqual(Post.objects.count(), 1)
        response = self.client.post(reverse('post_new'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), 1)


class PostUpdateViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.author = get_user_model().objects.create_user(
            username='author',
            email='author@email.com',
            password='secret'
        )
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )

        self.admin = get_user_model().objects.create_superuser(
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
        self.post = Post.objects.create(
            title='New Post',
            body='New content',
            author=self.author
        )
        self.post2 = Post.objects.create(
            title='Existing post',
            body='Existing content',
            author=self.author
        )

    def test_get_response_for_author(self):
        self.client.login(username='author', password='secret')
        response = self.client.get(reverse('post_edit', args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'form.html')

    def test_get_response_for_superuser(self):
        self.client.login(username='admin', password='supersecret')
        response = self.client.get(reverse('post_edit', args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'form.html')

    def test_get_response_for_anonymous_user(self):
        response = self.client.get(reverse('post_edit', args=[self.post.slug]))
        self.assertEqual(response.status_code, 403)

    def test_get_response_for_another_user(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('post_edit', args=[self.post.slug]))
        self.assertEqual(response.status_code, 403)

    def test_update_post_by_author(self):
        data = {'title': 'Post edited by author',
                'body': 'Edited content',
                'tags': [self.tag1.id]}

        posts = Post.objects.all()
        self.assertEqual(posts.count(), 2)

        self.client.login(username='author', password='secret')
        response = self.client.post(reverse('post_edit', args=[self.post.slug]), data)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(posts.count(), 2)
        self.assertFalse(posts.filter(title__exact='New Post'))
        self.assertTrue(posts.filter(title__exact='Post edited by author'))

        edited_post = posts.filter(title__exact='Post edited by author').first()

        self.assertEqual(edited_post.title, 'Post edited by author')
        self.assertEqual(edited_post.body, 'Edited content')
        self.assertEqual(edited_post.tags.count(), 1)
        self.assertEqual(edited_post.tags.get(id=self.tag1.id), self.tag1)
        self.assertEqual(edited_post.slug, slugify('Post edited by author'))

    def test_update_post_by_superuser(self):
        data = {'title': 'Post edited by admin',
                'body': 'Edited content',
                'tags': [self.tag1.id, self.tag2.id]}

        posts = Post.objects.all()
        self.assertEqual(posts.count(), 2)

        self.client.login(username='admin', password='supersecret')
        response = self.client.post(reverse('post_edit', args=[self.post.slug]), data)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(posts.count(), 2)
        self.assertFalse(posts.filter(title__exact='New Post'))
        self.assertTrue(posts.filter(title__exact='Post edited by admin'))

        edited_post = posts.filter(title__exact='Post edited by admin').first()

        self.assertEqual(edited_post.title, 'Post edited by admin')
        self.assertEqual(edited_post.body, 'Edited content')
        self.assertEqual(edited_post.tags.count(), 2)
        self.assertEqual(edited_post.tags.get(id=self.tag1.id), self.tag1)
        self.assertEqual(edited_post.tags.get(id=self.tag2.id), self.tag2)
        self.assertEqual(edited_post.slug, slugify('Post edited by admin'))

    def test_update_post_title_to_not_unique_fails(self):
        data = {'title': 'Existing post',
                'body': 'Edited content',
                'tags': [self.tag1.id, self.tag2.id]}

        self.client.login(username='author', password='secret')
        response = self.client.post(reverse('post_edit', args=[self.post.slug]), data)
        self.assertEqual(response.status_code, 200)
        post = Post.objects.filter(title__exact='Existing post').first()
        self.assertEqual(Post.objects.filter(title__exact='Existing post').count(), 1)
        self.assertEqual(post.body, 'Existing content')

    def test_update_post_set_title_value_new_fails(self):
        data = {'title': 'New',
                'body': 'Edited content',
                'tags': [self.tag1.id, self.tag2.id]}

        self.client.login(username='author', password='secret')
        response = self.client.post(reverse('post_edit', args=[self.post.slug]), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.filter(title__exact='New').first())
        self.assertTrue(Post.objects.filter(title__exact='Existing post').first())

    def test_update_post_without_title_fails(self):
        data = {'body': 'Edited content',
                'tags': [self.tag1.id, self.tag2.id]}

        self.client.login(username='author', password='secret')
        response = self.client.post(reverse('post_edit', args=[self.post.slug]), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Post.objects.filter(title__exact='Existing post').first())


class PostDeleteViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.author = get_user_model().objects.create_user(
            username='author',
            email='author@email.com',
            password='secret'
        )
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )

        self.admin = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@email.com',
            password='supersecret'
        )

        self.post = Post.objects.create(
            title='New Post',
            body='New content',
            author=self.author
        )

    def test_get_response_for_author(self):
        self.client.login(username='author', password='secret')
        response = self.client.get(reverse('post_delete', args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'form.html')

    def test_get_response_for_superuser(self):
        self.client.login(username='admin', password='supersecret')
        response = self.client.get(reverse('post_delete', args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'form.html')

    def test_get_response_for_anonymous_user(self):
        response = self.client.get(reverse('post_delete', args=[self.post.slug]))
        self.assertEqual(response.status_code, 403)

    def test_get_response_for_another_user(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('post_delete', args=[self.post.slug]))
        self.assertEqual(response.status_code, 403)

    def test_delete_post_by_author(self):
        posts = Post.objects.all()
        self.assertEqual(posts.count(), 1)

        self.client.login(username='author', password='secret')
        response = self.client.post(reverse('post_delete', args=[self.post.slug]))
        self.assertEqual(response.status_code, 302)

        self.assertEqual(posts.count(), 0)
        self.assertEqual(response.url, reverse('home'))

    def test_delete_post_by_superuser(self):
        posts = Post.objects.all()
        self.assertEqual(posts.count(), 1)

        self.client.login(username='admin', password='supersecret')
        response = self.client.post(reverse('post_delete', args=[self.post.slug]))
        self.assertEqual(response.status_code, 302)

        self.assertEqual(posts.count(), 0)
        self.assertEqual(response.url, reverse('home'))


class PostDetailViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.author = get_user_model().objects.create_user(
            username='author',
            email='author@email.com',
            password='secret'
        )
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )

        self.admin = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@email.com',
            password='supersecret'
        )

        self.post = Post.objects.create(
            title='New Post',
            body='New content',
            author=self.author
        )

    def test_get_response_for_anonymous_user(self):
        response = self.client.get(reverse('post_detail', args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post_detail.html')
        self.assertContains(response, self.post.body)
        self.assertContains(response, self.author.username)
        self.assertNotContains(response, 'Edit Post')
        self.assertNotContains(response, 'Delete Post')

    def test_get_response_for_user(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('post_detail', args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post_detail.html')
        self.assertContains(response, self.post.body)
        self.assertContains(response, self.author.username)
        self.assertContains(response, 'Edit Post')
        self.assertContains(response, 'Delete Post')

    def test_comment_create_by_anonymous_user(self):
        post = self.post
        data = {'name': 'tester',
                'email': 'test@test.com',
                'body': 'some text'}
        self.assertEqual(post.comments.count(), 0)
        response = self.client.post(reverse('post_detail', args=[self.post.slug]), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(post.comments.count(), 1)
        comment = post.comments.last()
        self.assertEqual(comment.name, 'tester')
        self.assertEqual(comment.email, 'test@test.com')
        self.assertEqual(comment.body, 'some text')
        self.assertEqual(comment.author_status, 'anonymous')

    def test_comment_create_by_anonymous_user_without_required_data_fails(self):
        post = self.post
        data = {'email': 'test@test.com',
                'body': 'some text'}
        response = self.client.post(reverse('post_detail', args=[self.post.slug]), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post.comments.count(), 0)


    def test_comment_create_by_user(self):
        post = self.post
        self.client.login(username='testuser', password='secret')
        data = {
            'body': 'some text'
        }
        self.assertEqual(post.comments.count(), 0)
        response = self.client.post(reverse('post_detail', args=[self.post.slug]), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(post.comments.count(), 1)
        comment = post.comments.last()
        self.assertEqual(comment.name, self.user.username)
        self.assertEqual(comment.email, self.user.email)
        self.assertEqual(comment.body, 'some text')
        self.assertEqual(comment.author_status, 'user')

    def test_comment_create_by_superuser(self):
        post = self.post
        self.client.login(username='admin', password='supersecret')
        data = {
            'body': 'some text'
        }
        self.assertEqual(post.comments.count(), 0)
        response = self.client.post(reverse('post_detail', args=[self.post.slug]), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(post.comments.count(), 1)
        comment = post.comments.last()
        self.assertEqual(comment.name, self.admin.username)
        self.assertEqual(comment.email, self.admin.email)
        self.assertEqual(comment.body, 'some text')
        self.assertEqual(comment.author_status, 'staff')


class PostListViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.author = get_user_model().objects.create_user(
            username='author',
            email='author@email.com',
            password='secret'
        )
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )
        self.tag1 = Tag.objects.create(
            title='tag1'
        )
        self.tag2 = Tag.objects.create(
            title='tag2'
        )

        self.post1 = Post.objects.create(
            title='Post 1',
            body='Python 2',
            author=self.author
        )
        time.sleep(0.01)
        self.post2 = Post.objects.create(
            title='Post 2',
            body='Python 3',
            author=self.user
        )
        self.post2.tags.set([self.tag1])
        time.sleep(0.01)
        self.post3 = Post.objects.create(
            title='Post 3',
            body='Django',
            author=self.author
        )
        self.post3.tags.set([self.tag1, self.tag2])
        time.sleep(0.01)
        self.post4 = Post.objects.create(
            title='Post 4',
            body='Aiohttp',
            author=self.author
        )

    def test_get_response_for_anonymous_user(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertEqual(len(response.context['posts']), 3)
        self.assertEqual(response.context['posts_count'], 4)
        self.assertContains(response, self.post4.title)
        self.assertContains(response, self.post3.title)
        self.assertContains(response, self.post2.title)
        self.assertContains(response, self.tag1.title)
        self.assertContains(response, self.tag2.title)
        self.assertContains(response, self.author.username)
        self.assertContains(response, self.user.username)
        self.assertNotContains(response, self.post1.title)
        self.assertNotContains(response, 'New Post')

    def test_get_response_for_user(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertEqual(len(response.context['posts']), 3)
        self.assertEqual(response.context['posts_count'], 4)
        self.assertContains(response, self.post4.title)
        self.assertContains(response, self.post3.title)
        self.assertContains(response, self.post2.title)
        self.assertContains(response, self.tag1.title)
        self.assertContains(response, self.tag2.title)
        self.assertContains(response, self.author.username)
        self.assertContains(response, self.user.username)
        self.assertNotContains(response, self.post1.title)
        self.assertContains(response, 'New Post')

    def test_filter_posts_by_tag(self):
        response = self.client.get(reverse('tag_detail', args=['tag1']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 2)
        self.assertContains(response, self.post3.title)
        self.assertContains(response, self.post2.title)
        self.assertContains(response, self.tag1.title)
        self.assertNotContains(response, self.post1.title)
        self.assertNotContains(response, self.post4.title)

    def test_filter_posts_by_author(self):
        response = self.client.get(reverse('posts_by_author', args=[self.author.username]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 3)
        self.assertContains(response, self.post4.title)
        self.assertContains(response, self.post3.title)
        self.assertContains(response, self.post1.title)
        self.assertNotContains(response, self.post2.title)

    def test_filter_posts_by_search_query(self):
        response = self.client.get(reverse('home'), {'search': 'python'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 2)
        self.assertContains(response, self.post1.title)
        self.assertContains(response, self.post2.title)
        self.assertNotContains(response, self.post3.title)
        self.assertNotContains(response, self.post4.title)


class TagViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )
        self.admin = get_user_model().objects.create_superuser(
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

    def test_create_tag_by_anonymous_user_fails(self):
        response = self.client.get(reverse('tag_new'))
        self.assertEqual(response.status_code, 302)
        count = Tag.objects.count()
        self.assertEqual(count, 2)
        data = {'title': 'new tag'}
        response2 = self.client.post(reverse('tag_new'), data=data)
        self.assertEqual(response2.status_code, 302)
        self.assertEqual(count, 2)

    def test_update_tag_by_anonymous_user_fails(self):
        response = self.client.get(reverse('tag_edit', args=[self.tag1.slug]))
        self.assertEqual(response.status_code, 403)
        data = {'title': 'new tag'}
        response2 = self.client.post(reverse('tag_edit', args=[self.tag1.slug]), data)
        self.assertEqual(response2.status_code, 403)
        self.assertFalse(Tag.objects.filter(title__exact='new tag').first())
        self.assertTrue(Tag.objects.filter(title__exact='tag1').first())

    def test_delete_tag_by_anonymous_user_fails(self):
        response = self.client.get(reverse('tag_delete', args=[self.tag1.slug]))
        self.assertEqual(response.status_code, 403)
        response2 = self.client.post(reverse('tag_delete', args=[self.tag1.slug]))
        self.assertEqual(response2.status_code, 403)
        self.assertTrue(Tag.objects.filter(title__exact='tag1').first())

    def test_create_tag_by_user(self):
        self.client.login(username='testuser', password='secret')
        data = {'title': 'new tag'}
        response = self.client.post(reverse('tag_new'), data)
        self.assertEqual(response.status_code, 302)
        count = Tag.objects.count()
        self.assertEqual(count, 3)
        self.assertTrue(Tag.objects.filter(title__exact='new tag').first())

    def test_update_tag_by_user_fails(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('tag_edit', args=[self.tag1.slug]))
        self.assertEqual(response.status_code, 403)
        data = {'title': 'new tag'}
        response2 = self.client.post(reverse('tag_edit', args=[self.tag1.slug]), data)
        self.assertEqual(response2.status_code, 403)
        self.assertFalse(Tag.objects.filter(title__exact='new tag').first())
        self.assertTrue(Tag.objects.filter(title__exact='tag1').first())

    def test_delete_tag_by_user_fails(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('tag_delete', args=[self.tag1.slug]))
        self.assertEqual(response.status_code, 403)
        response2 = self.client.post(reverse('tag_delete', args=[self.tag1.slug]))
        self.assertEqual(response2.status_code, 403)
        self.assertTrue(Tag.objects.filter(title__exact='tag1').first())

    def test_update_tag_by_superuser(self):
        self.client.login(username='admin', password='supersecret')
        response = self.client.get(reverse('tag_edit', args=[self.tag1.slug]))
        self.assertEqual(response.status_code, 200)
        data = {'title': 'new tag'}
        response2 = self.client.post(reverse('tag_edit', args=[self.tag1.slug]), data)
        self.assertEqual(response2.status_code, 302)
        self.assertTrue(Tag.objects.filter(title__exact='new tag').first())
        self.assertFalse(Tag.objects.filter(title__exact='tag1').first())

    def test_delete_tag_by_superuser(self):
        self.client.login(username='admin', password='supersecret')
        self.assertEqual(Tag.objects.count(), 2)
        response = self.client.post(reverse('tag_delete', args=[self.tag1.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Tag.objects.filter(title__exact='tag1').first())
        self.assertEqual(Tag.objects.count(), 1)

    def test_create_tag_without_title_fails(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.post(reverse('tag_new'))
        self.assertEqual(response.status_code, 200)
        count = Tag.objects.count()
        self.assertEqual(count, 2)
        self.assertFalse(Tag.objects.filter(title__exact='new').first())

    def test_create_tag_set_title_value_new_fails(self):
        self.client.login(username='testuser', password='secret')
        data = {'title': 'new'}
        response = self.client.post(reverse('tag_new'), data)
        self.assertEqual(response.status_code, 200)
        count = Tag.objects.count()
        self.assertEqual(count, 2)
        self.assertFalse(Tag.objects.filter(title__exact='new').first())

    def test_create_tag_with_not_unique_title_fails(self):
        self.client.login(username='testuser', password='secret')
        data = {'title': 'tag1'}
        response = self.client.post(reverse('tag_new'), data)
        self.assertEqual(response.status_code, 200)
        count = Tag.objects.count()
        self.assertEqual(count, 2)

    def test_update_tag_set_title_value_new_fails(self):
        self.client.login(username='admin', password='supersecret')
        data = {'title': 'new'}
        response = self.client.post(reverse('tag_edit', args=[self.tag1.slug]), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Tag.objects.filter(title__exact='new').first())
        self.assertTrue(Tag.objects.filter(title__exact='tag1').first())

    def test_update_tag_on_not_unique_title_fails(self):
        self.client.login(username='admin', password='supersecret')
        data = {'title': 'tag2'}
        response = self.client.post(reverse('tag_edit', args=[self.tag1.slug]), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Tag.objects.filter(title__exact='tag1').first())
