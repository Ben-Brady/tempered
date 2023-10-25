from tempered.preprocess.css import preprocess_style_tags, minify_css
import bs4
from rcssmin import cssmin


def test_preprocess_css():
    HTML = """
    <div>
    </div>

    <style global>
        body {
            background: black;
        }
    </style>

    <style>
        div {
            color: red;
        }
    </style>
    """
    html, style = preprocess_style_tags(HTML)

    assert minify_css("body {background: black;}") in style

    soup = bs4.BeautifulSoup(html, "html.parser")
    div = soup.find("div")
    assert div and div.has_attr("class")
    print(html, style)


def test_preprocess_scope_class_applied():
    HTML = """
    <a>
        <b>
            <c>
            </c>
        </b>
    </a>

    <style>
        div {
            color: red;
        }

        div a c{
            color: blue;
        }
    </style>
    """
    html, style = preprocess_style_tags(HTML)

