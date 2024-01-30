import textwrap
import warnings
import typing_extensions as t
from .. import errors

try:
    import sass
except ImportError:
    sass = None


def transform_sass(css: str, lang: t.Literal["sass", "scss"]) -> str:
    if sass is None:
        warnings.warn(
            message="sass support not installed, run `pip install tempered[sass]`",
            category=errors.ParsingWarning,
        )
        return ""

    if lang == "sass":
        css = textwrap.dedent(css)
        indented = True
    else:
        indented = False

    return sass.compile(
        string=css,
        indented=indented,  # sass/css rules
        output_style="compressed",
    )
