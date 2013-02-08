from ella.core.custom_urls import resolver

from .models import Wiki
from .urls import custom_url_patterns

resolver.register(custom_url_patterns, model=Wiki)

