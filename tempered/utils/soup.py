import bs4
from importlib.util import find_spec

lxml_installed = find_spec("lxml") is not None
if lxml_installed:
    html_parser = "lxml"
else:
    html_parser = "html.parser"


def HtmlSoup(markup: str):
    return bs4.BeautifulSoup(markup, html_parser)
