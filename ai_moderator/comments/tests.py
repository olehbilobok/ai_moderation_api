from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse

from comments.models import Comment
from comments.views import CommentsAnalyticsView
from posts.models import Post


class TestCommentsAnalyticsView(APITestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@gmail.com',
            password='testpass'
        )

        # Create a test post
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post',
            user=self.user
        )

        # Set up APIRequestFactory and JWT token
        self.factory = APIRequestFactory()
        self.view = CommentsAnalyticsView.as_view()
        self.url = reverse('comments_analytics')

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # Create comments linked to the post
        self.comment1 = Comment.objects.create(
            content='This is a test comment',
            user=self.user,
            post=self.post,  # Link to the post
            is_blocked=False
        )
        self.comment2 = Comment.objects.create(
            content='This comment is blocked',
            user=self.user,
            post=self.post,  # Link to the post
            is_blocked=True
        )

    def test_get_analytics(self):
        """Test retrieving analytics without date filtering."""
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user, token=self.access_token)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_comments', response.data[0])
        self.assertIn('blocked_comments', response.data[0])

    def test_get_analytics_with_date_range(self):
        """Test retrieving analytics within a specific date range."""
        date_from = (timezone.now() - timezone.timedelta(days=1)).date()
        date_to = (timezone.now() + timezone.timedelta(days=1)).date()
        url_with_dates = f'{self.url}?date_from={date_from}&date_to={date_to}'

        request = self.factory.get(url_with_dates)
        force_authenticate(request, user=self.user, token=self.access_token)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # One result expected for today's date range

    def test_get_analytics_no_comments_in_date_range(self):
        """Test retrieving analytics where no comments exist in the specified date range."""
        date_from = '1800-01-01'
        date_to = '1800-12-31'
        url_with_dates = f'{self.url}?date_from={date_from}&date_to={date_to}'

        request = self.factory.get(url_with_dates)
        force_authenticate(request, user=self.user, token=self.access_token)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
