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
            message='sass support not installed, run "pip install tempered[sass]"',
            category=errors.ParsingWarning,
        )
        return ""

    is_indented = lang == "sass"
    if is_indented:
        css = textwrap.dedent(css)

    return sass.compile(
        string=css,
        indented=is_indented,  # sass/css rules
        output_style="compressed",
    )
