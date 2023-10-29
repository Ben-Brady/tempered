from tempered.preprocess.css import generate_scoped_styles, minify_css
import bs4
from rcssmin import cssmin


def test_preprocess_extracts_style_tags():
    HTML = """
    <style global>
        body { background: black; }
    </style>
    <style>
        div { color: red;}
    </style>
    """
    html, _ = generate_scoped_styles(HTML)
    soup = bs4.BeautifulSoup(html, "html.parser")
    assert len(soup.find_all("style")) == 0


def test_preprocess_extracts_global_css():
    HTML = """
    <style global>
        body {
            background: black;
        }
    </style>
    """
    _, style = generate_scoped_styles(HTML)
    assert minify_css(style) == "body{background:black}"


def test_preprocess_scopes_css():
    HTML = """
    <div></div>

    <style>
        div {
            background: black;
        }
    </style>
    """
    html, style = generate_scoped_styles(HTML)
    soup = bs4.BeautifulSoup(html, "html.parser")
    div = soup.find("div")

    assert div and isinstance(div, bs4.element.Tag), "div should exist"
    assert "class" in div.attrs, "div should have a scope class"
    assert "{background:black}" in minify_css(style), "css should be preserved"


def test_preprocess_doesnt_override_clases():
    HTML = """
    <div class="test">
    </div>

    <style>
        div { background: black; }
    </style>
    """
    html, style = generate_scoped_styles(HTML)
    soup = bs4.BeautifulSoup(html, "html.parser")
    div = soup.find("div")
    assert div and isinstance(div, bs4.element.Tag), "div should exist"
    assert "class" in div.attrs, "div should have a scope class"

    if isinstance(div.attrs["class"], list):
        classes = div.attrs["class"]
    else:
        classes = div.attrs["class"].split(" ")

    assert "test" in classes, "div should have the original class"
    assert len(classes) == 2, "div should have scope class"
