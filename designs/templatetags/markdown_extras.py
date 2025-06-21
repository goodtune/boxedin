from functools import partial

import bleach
from bleach.linkifier import LinkifyFilter
from django import template
from django.utils.safestring import mark_safe
from markdown import markdown

from markdownfield.models import EXTENSIONS, EXTENSION_CONFIGS
from markdownfield.util import blacklist_link, format_link
from markdownfield.validators import VALIDATOR_STANDARD

register = template.Library()


@register.filter(name="markdown_to_html")
def markdown_to_html(value: str) -> str:
    """Render markdown text as safe HTML."""
    if not value:
        return ""

    dirty = markdown(text=value, extensions=EXTENSIONS, extension_configs=EXTENSION_CONFIGS)

    if VALIDATOR_STANDARD.sanitize:
        if VALIDATOR_STANDARD.linkify:
            cleaner = bleach.Cleaner(
                tags=VALIDATOR_STANDARD.allowed_tags,
                attributes=VALIDATOR_STANDARD.allowed_attrs,
                css_sanitizer=VALIDATOR_STANDARD.css_sanitizer,
                filters=[partial(LinkifyFilter, callbacks=[format_link, blacklist_link])],
            )
        else:
            cleaner = bleach.Cleaner(
                tags=VALIDATOR_STANDARD.allowed_tags,
                attributes=VALIDATOR_STANDARD.allowed_attrs,
                css_sanitizer=VALIDATOR_STANDARD.css_sanitizer,
            )
        clean = cleaner.clean(dirty)
    else:
        clean = dirty

    return mark_safe(clean)
