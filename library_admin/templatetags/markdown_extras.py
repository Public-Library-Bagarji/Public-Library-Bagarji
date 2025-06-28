from django import template
import markdown

template.Library()
register = template.Library()

@register.filter(is_safe=True)
def markdownify(text):
    if not text:
        return ""
    return markdown.markdown(text, extensions=["extra", "nl2br", "sane_lists"]) 