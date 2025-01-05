import bs4
from tempered.src.css.extract import extract_css_from_soup
from tempered.src.css.postprocess import minify_css
from tempered.src.utils.soup import HtmlSoup


def test_preprocess_extracts_style_tags():
    soup = HtmlSoup("""
    <style global>
        body { background: black; }
    </style>
    <style>
        div { color: red; }
    </style>
    """)
    extract_css_from_soup(soup)
    assert len(soup.find_all("style")) == 0


def test_preprocess_extracts_global_css():
    soup = HtmlSoup("""
    <style global>
        body {
            background: black;
        }
    </style>
    """)
    css = extract_css_from_soup(soup)
    assert minify_css(css) == "body{background:black}"


def test_preprocess_scopes_css():
    soup = HtmlSoup("""
    <div></div>

    <style>
        div {
            background: black;
        }
    </style>
    """)
    css = extract_css_from_soup(soup)
    div = soup.find("div")

    assert div and isinstance(div, bs4.element.Tag), "div should exist"
    assert "class" in div.attrs, "div should have a scope class"
    assert "{background:black}" in minify_css(css), "css should be preserved"


def test_preprocess_doesnt_override_clases():
    soup = HtmlSoup("""
    <div class="test">
    </div>

    <style>
        div { background: black; }
    </style>
    """)
    extract_css_from_soup(soup)

    div = soup.find("div")
    assert div and isinstance(div, bs4.element.Tag), "div should exist"
    assert "class" in div.attrs, "div should have a scope class"

    if isinstance(div.attrs["class"], list):
        classes = div.attrs["class"]
    else:
        classes = div.attrs["class"].split(" ")

    assert "test" in classes, "div should have the original class"
    assert len(classes) == 2, "div should have scope class"
