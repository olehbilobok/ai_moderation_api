import re

from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai
import os


genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel(model_name='gemini-1.5-flash')


class AIModerator:

    def __init__(self, prompt):
        self.prompt = prompt

    @staticmethod
    def get_response(prompt):
        response = model.generate_content(
            prompt,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        return response.text

    def check_profanity(self):
        prompt = (f'Does the following expression have the profanity content? '
                  f'Expression: {self.prompt}. I need you answer the question with only one word "Yes" or "No".')
        try:
            profanity = self.clean_content(self.get_response(prompt))
            return True if profanity == 'Yes' else False
        except Exception:
            return False

    def generate_comment(self, post, comment):
        context = self.create_context(post, comment)
        chat = model.start_chat(history=context)
        response = chat.send_message(comment.content)
        cleaned_response = self.clean_content(response.text)
        return f'Dear {comment.user.username}! {cleaned_response}'

    @staticmethod
    def create_context(post, comment):
        context = list()
        context.append({'role': 'user', 'parts': post.content})

        def collect_comment_chain(comment):
            if comment.parent:
                collect_comment_chain(comment.parent)
                role = 'model' if post.user.id != comment.user.id else 'user'
                context.append({'role': role, 'parts': comment.parent.content})

        if comment.parent:
            collect_comment_chain(comment)

        return context

    @staticmethod
    def clean_content(response):
        cleaned = response.strip().replace('\n', ' ').replace('  ', ' ')
        cleaned = re.sub(r'\*+', '', cleaned)
        return cleaned
