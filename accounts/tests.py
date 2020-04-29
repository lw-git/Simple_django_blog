from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class SignupViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@email.com',
            password='secret'
        )

    def test_get_response_for_anonymous_user(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('signup.html')

    def test_get_response_for_authenticated_user(self):
        self.client.login(username='testuser', password='secret')
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 302)

    def test_register_user(self):
        self.assertEqual(get_user_model().objects.count(), 1)
        data = {
            'username': 'test',
            'password1': 'secret!!!',
            'password2': 'secret!!!'
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_user_model().objects.count(), 2)

        new_user = get_user_model().objects.get(username='test')
        self.assertEqual(new_user.username, 'test')
        self.assertTrue(new_user.check_password('secret!!!'))

    def test_register_user_without_required_data_fails(self):
        self.assertEqual(get_user_model().objects.count(), 1)
        data = {
            'password1': 'secret!!!',
            'password2': 'secret!!!'
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].errors['username'].data[0].message,
            'This field is required.'
        )
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_register_user_with_short_password_fail(self):
        self.assertEqual(get_user_model().objects.count(), 1)
        data = {
            'username': 'test',
            'password1': 'secret',
            'password2': 'secret'
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].errors['password2'].data[0].message,
            'This password is too short. It must contain at least %(min_length)d characters.'
        )
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_register_user_with_not_unique_username_fail(self):
        self.assertEqual(get_user_model().objects.count(), 1)
        data = {
            'username': 'testuser',
            'password1': 'secret!!!',
            'password2': 'secret!!!'
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].errors['username'].data[0].message,
            'A user with that username already exists.'
        )
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_register_user_with_different_passwords_fail(self):
        self.assertEqual(get_user_model().objects.count(), 1)
        data = {
            'username': 'test',
            'password1': 'secret!!!',
            'password2': 'dhndohndohn'
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(
            response.context['form'].errors['password2'].data[0].message,
            "The two password fields didn't match."
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_user_model().objects.count(), 1)
