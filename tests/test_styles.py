from utils import build_template
import bs4


def test_template_add_styles():
    CSS_KEY = "TEMPERED"
    CSS = f"a{{content:'{CSS_KEY}';}}"
    func = build_template(f"""
        <a>
            Bar!
        </a>
        <style>
            {CSS}
        </style>
    """)

    html = func(with_styles=True)
    assert CSS_KEY in html


def test_template_wont_add_styles():
    CSS_KEY = "TEMPERED"
    CSS = f"a{{content:'{CSS_KEY}';}}"
    func = build_template(f"""
        <a>
            Bar!
        </a>
        <style>
            {CSS}
        </style>
    """)

    html = func(with_styles=False)
    assert CSS_KEY not in html


def test_template_places_styles():
    CSS_KEY = "TEMPERED"
    CSS = f"a{{content:'{CSS_KEY}';}}"
    func = build_template(f"""
        <head>
            {{% styles %}}
        </head>
        <style>
            {CSS}
        </style>
    """)

    html = func(with_styles=True)
    soup = bs4.BeautifulSoup(html, "html.parser")
    assert CSS_KEY in soup.find("style").text
