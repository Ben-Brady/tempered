import bs4

html_parser = "html.parser"


def HtmlSoup(html: str):
    return bs4.BeautifulSoup(html, html_parser)
