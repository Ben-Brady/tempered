from tempered import Tempered
from dataclasses import dataclass
from datetime import datetime
import bs4

templates = Tempered()

@dataclass
class Comment:
    author: str
    created_at: datetime
    text: str


if __name__ == "__main__":
    templates.add_template_from_string("comment", """
    {%param comment: Comment %}
    <div>
        <span class="header">
            {{ comment.author }} - {{ comment.created_at.strftime("%d/%m/%y") }}
        </span>
        <span class="body">
            {{ comment.text }}
        </span>
    </div>

    <style>
    div {
        width: 10rem
        height: fit-content;
    }
    .header {
        width: 100%;
        height: 1.5rem;
    }
    .body {
        width: 100%;
        height: fit-content;
    }
    </style>
    """)

    components = templates.build_static()
    comment = Comment(
        author="Ben Brady",
        created_at=datetime.now(),
        text="This library is pretty goated",
    )

    html = components.comment(comment=comment)
    soup = bs4.BeautifulSoup(html, "html.parser")
    print(soup.prettify())
