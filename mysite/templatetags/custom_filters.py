from django import template
import re
from django.utils.safestring import mark_safe
from django import template

register = template.Library()

@register.filter
def highlight_query(text, query):
    """Highlights occurrences of `query` in `text`."""
    if not query:
        return text
    highlighted = re.sub(f"({re.escape(query)})", r"<mark>\1</mark>", text, flags=re.IGNORECASE)
    return mark_safe(highlighted)

@register.filter
def is_video(file_name):
    return file_name.lower().endswith(('.mp4', '.mov', '.avi'))

@register.filter
def is_image(file_name):
    return file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))

@register.filter
def is_audio(file_name):
    return file_name.lower().endswith(('.mp3', '.wav', '.aac'))

@register.filter
def is_text(file_name):
    return file_name.lower().endswith(('.txt', '.pdf', '.docx'))