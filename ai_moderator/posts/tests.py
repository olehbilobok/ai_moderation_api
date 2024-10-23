from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from posts.models import Post
from posts.views import PostAPIList, PostAPIDetail


class TestPostAPIList(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@gmail.com',
            password='testpass'
        )
        self.factory = APIRequestFactory()
        self.view = PostAPIList.as_view()
        self.url = reverse('post_list')
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def test_list_posts(self):
        request = self.factory.get(self.url)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('posts.views.AIModerator.check_profanity', return_value=False)
    def test_post_create(self, mock_check_profanity):
        test_post = {
            'title': 'test_title',
            'content': 'test_content',
        }
        request = self.factory.post(self.url, test_post, format='json')
        force_authenticate(request, user=self.user, token=self.access_token)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'],  'test_title')

    @patch('posts.views.AIModerator.check_profanity', return_value=True)
    def test_post_create_blocked(self, mock_check_profanity):
        test_post = {
            'title': 'test_title',
            'content': 'test_content',
        }
        request = self.factory.post(self.url, test_post, format='json')
        force_authenticate(request, user=self.user, token=self.access_token)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Post contains inappropriate content.")


class TestPostAPIDetail(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@gmail.com',
            password='testpass'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='otheruser@gmail.com',
            password='testpass'
        )
        self.post = Post.objects.create(
            title='test_title',
            content='test_content',
            user=self.user
        )
        self.factory = APIRequestFactory()
        self.view = PostAPIDetail.as_view()
        self.url = reverse('post_detail', kwargs={'pk': self.post.pk})

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def test_get_post(self):
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user, token=self.access_token)
        response = self.view(request, pk=self.post.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('posts.views.AIModerator.check_profanity', return_value=False)
    def test_put_post(self, mock_check_profanity):
        updated_data = {
            'title': 'updated_title',
            'content': 'updated_content',
        }
        request = self.factory.put(self.url, updated_data, format='json')
        force_authenticate(request, user=self.user, token=self.access_token)
        response = self.view(request, pk=self.post.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'updated_title')

    @patch('posts.views.AIModerator.check_profanity', return_value=True)
    def test_put_post_blocked(self, mock_check_profanity):
        updated_data = {
            'title': 'updated_title',
            'content': 'blocked_content',
        }
        request = self.factory.put(self.url, updated_data, format='json')
        force_authenticate(request, user=self.user, token=self.access_token)
        response = self.view(request, pk=self.post.pk)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Post cannot be modified because contains inappropriate content.")

    def test_delete_post(self):
        request = self.factory.delete(self.url)
        force_authenticate(request, user=self.user, token=self.access_token)
        response = self.view(request, pk=self.post.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())
