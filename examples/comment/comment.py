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


templates.add_template("./Comment.html")
components = templates.build_static()
comment = Comment(
    author="Ben Brady",
    created_at=datetime.now(),
    text="This library is pretty goated",
)
html = components.Comment(comment=comment)
soup = bs4.BeautifulSoup(html, "html.parser")
print(soup.prettify())
