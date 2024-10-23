from threading import Timer

from ai_moderator.integrations.gemini_api import AIModerator
from comments.models import Comment


class AutoReplyService:
    @staticmethod
    def schedule_auto_reply(post, comment):
        if post.is_auto_reply_enabled:
            delay = post.reply_delay
            Timer(delay, AutoReplyService.reply_to_comment, [post, comment]).start()

    @staticmethod
    def reply_to_comment(post, comment):
        response = AIModerator(comment.content).generate_comment(post, comment)
        Comment.objects.create(post=post, user=post.user, content=response, parent=comment)
