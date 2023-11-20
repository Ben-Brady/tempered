from typing import Self, dataclass_transform
from pathlib import Path

class PostModel:
    ...


@dataclass_transform()
class Template:
    ...


class TemplateBody:
    html: str|Path = ""

    scss: str|Path|None = None
    css: str|Path|None = None

    typescript: str|Path|None = None
    script: str|Path|None = None


    @classmethod
    def from_str(cls, body: str) -> Self:
        ...


    @classmethod
    def from_file(cls, file: str | Path) -> Self:
        file = Path(file)
        return cls.from_str(file.read_text())


class Post(Template):
    post: PostModel

    class Body(TemplateBody):
        html = """
            {!styles!}
            {<Post
                post=post
            >}
        """

        scss = """
            body {
                color: red;
            }
        """

        typescript = """
            console.log("Hello, world!");
        """

