"""
URL configuration for ai_moderator project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from comments.views import CommentAPIList, CommentsAnalyticsView
from posts.views import PostAPIList, PostAPIDetail
from users.views import UserRegistration

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register', UserRegistration.as_view(), name='user_register'),
    path('api/posts', PostAPIList.as_view(), name='post_list'),
    path('api/posts/<int:pk>', PostAPIDetail.as_view(), name='post_detail'),
    path('api/posts/<int:post_pk>/comments', CommentAPIList.as_view(), name='comment_post_list'),
    path('api/posts/<int:post_pk>/comments/<int:comment_pk>', CommentAPIList.as_view(), name='comment_comment_list'),
    path('api/comments-daily-breakdown', CommentsAnalyticsView.as_view(), name='comments_analytics'),
]
