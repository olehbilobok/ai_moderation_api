from django.db.models import Q
from django.db.models import Count
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_moderator.integrations.gemini_api import AIModerator
from ai_moderator.services.auto_reply import AutoReplyService
from comments.models import Comment
from comments.serializers import CommentSerializer
from posts.models import Post


class CommentAPIList(APIView):

    def get(self, request, post_pk):
        comments = Comment.objects.filter(post_id=post_pk, is_blocked=False, parent=None)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, post_pk, comment_pk=None):
        try:
            post = Post.objects.get(id=post_pk)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        parent_comment = None
        if comment_pk:
            try:
                parent_comment = Comment.objects.get(id=comment_pk, post=post)
            except Comment.DoesNotExist:
                return Response({'error': 'Parent comment not found'}, status=status.HTTP_404_NOT_FOUND)

        request.data['user'] = request.user.id
        request.data['post'] = post_pk
        request.data['parent'] = parent_comment.id if parent_comment else None
        content = request.data['content']

        is_blocked = AIModerator(content).check_profanity()
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            if is_blocked:
                serializer.save(is_blocked=is_blocked)
                return Response({"error": "Comment contains inappropriate content."},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                comment = serializer.save()
                AutoReplyService.schedule_auto_reply(post, comment)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentsAnalyticsView(APIView):

    def get(self, request):
        date_from = request.query_params.get('date_from', '1900-01-01')
        date_to = request.query_params.get('date_to', '3000-01-01')

        analytics = Comment.objects.filter(created_at__range=[date_from, date_to]).values('created_at__date').annotate(
            total_comments=Count('id'),
            blocked_comments=Count('id', filter=Q(is_blocked=True))
        )

        return Response(analytics, status=status.HTTP_200_OK)
