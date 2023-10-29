from tempered import Tempered
from dataclasses import dataclass
from datetime import datetime

templates = Tempered()

@dataclass
class Comment:
    author: str
    created_at: datetime
    text: str


if __name__ == "__main__":
    templates.add_template("comment", """
    {!param comment: Comment !}
    <div>
        <span>
            {{ comment.author }} - {{ comment.created_at.strftime("%d/%m/%y") }}
        </span>
        <span>
            {{ comment.text }}
        </span>
    </div>
    """)
    templates.register_type(Comment)

    components = templates.build_static()
    comment = Comment(
        author="Ben Brady",
        created_at=datetime.now(),
        text="This library is pretty goated",
    )
    print(components.comment(comment=comment))
