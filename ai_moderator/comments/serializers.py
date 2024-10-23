from rest_framework import serializers

from comments.models import Comment


class ReplySerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'content', 'created_at', 'post', 'user', 'parent', 'replies')

    def get_replies(self, obj):
        # Return a serialized list of replies
        return ReplySerializer(obj.replies.all(), many=True).data

class CommentSerializer(serializers.ModelSerializer):
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'content', 'created_at', 'post', 'user', 'parent', 'replies')