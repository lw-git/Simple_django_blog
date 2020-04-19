from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


from .models import Tag


class TagModelTests(TestCase):

    def setUp(self):
        self.tag = Tag.objects.create(
            title='Super Tag'
        )

    def test_string_representation(self):
        self.assertEqual(str(self.tag), self.tag.title)

    def test_tag_slug(self):
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
