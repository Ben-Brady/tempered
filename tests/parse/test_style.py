from tempered.parser.css import tranform_css, minify_css
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
    scoped = tranform_css(HTML)
    soup = bs4.BeautifulSoup(scoped.html, "html.parser")
    assert len(soup.find_all("style")) == 0


def test_preprocess_extracts_global_css():
    HTML = """
    <style global>
        body {
            background: black;
        }
    </style>
    """
    scoped = tranform_css(HTML)
    assert minify_css(scoped.css) == "body{background:black}"


def test_preprocess_scopes_css():
    HTML = """
    <div></div>

    <style>
        div {
            background: black;
        }
    </style>
    """
    scoped = tranform_css(HTML)
    soup = bs4.BeautifulSoup(scoped.html, "html.parser")
    div = soup.find("div")

    assert div and isinstance(div, bs4.element.Tag), "div should exist"
    assert "class" in div.attrs, "div should have a scope class"
    assert "{background:black}" in minify_css(scoped.css), "css should be preserved"


def test_preprocess_doesnt_override_clases():
    HTML = """
    <div class="test">
    </div>

    <style>
        div { background: black; }
    </style>
    """
    scoped = tranform_css(HTML)
    soup = bs4.BeautifulSoup(scoped.html, "html.parser")
    div = soup.find("div")
    assert div and isinstance(div, bs4.element.Tag), "div should exist"
    assert "class" in div.attrs, "div should have a scope class"

    if isinstance(div.attrs["class"], list):
        classes = div.attrs["class"]
    else:
        classes = div.attrs["class"].split(" ")

    assert "test" in classes, "div should have the original class"
    assert len(classes) == 2, "div should have scope class"
