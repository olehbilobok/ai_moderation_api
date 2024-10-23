from rest_framework import serializers

from comments.serializers import CommentSerializer
from posts.models import Post


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'created_at', 'user', 'comments')
