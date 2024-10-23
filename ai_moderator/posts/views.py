from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_moderator.integrations.gemini_api import AIModerator
from posts.models import Post
from posts.permissions import IsOwnerOrReadOnly
from posts.serializers import PostSerializer


class PostAPIList(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        posts = Post.objects.filter(is_blocked=False)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        request.data['user'] = request.user.id
        content = request.data.get('content')

        reply_delay = request.query_params.get('reply_delay', 0)
        auto_reply = request.query_params.get('auto_reply', 'false').lower() == 'true'

        is_blocked = AIModerator(content).check_profanity()
        serializer = PostSerializer(data=request.data)

        if serializer.is_valid():
            if is_blocked:
                serializer.save(is_blocked=is_blocked)
                return Response({"error": "Post contains inappropriate content."},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer.save(reply_delay=reply_delay, is_auto_reply_enabled=auto_reply)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostAPIDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )

    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        post = self.get_object(pk)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def put(self, request, pk):
        request.data['user'] = request.user.id
        content = request.data.get('content')
        post = self.get_object(pk)
        self.check_object_permissions(request, post)

        reply_delay = request.query_params.get('reply_delay', 0)
        auto_reply = request.query_params.get('auto_reply', 'false').lower() == 'true'

        is_blocked = AIModerator(content).check_profanity()
        if is_blocked:
            return Response({"error": "Post cannot be modified because contains inappropriate content."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = PostSerializer(instance=post, data=request.data)
        if serializer.is_valid():
            serializer.save(reply_delay=reply_delay, is_auto_reply_enabled=auto_reply)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = self.get_object(pk)
        self.check_object_permissions(request, post)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
