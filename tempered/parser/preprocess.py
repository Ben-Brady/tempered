from ..preprocess import minify_html
from string import whitespace


def preprocess_html(html: str) -> str:
    html = html.strip(whitespace)
    html = minify_html(html)
    return html
