from ... import errors
import typing_extensions as t
import warnings
import textwrap
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
        css = remove_shared_ident(css)
        return sass.compile(
            string=css,
            output_style="compressed",
            indented=True,  # sass rules
        )
    else:
        return sass.compile(
            string=css,
            output_style="compressed",
            indented=False,  # scss rules
        )


def remove_shared_ident(css: str) -> str:
    lines = css.split("\n")
    content_lines = [line for line in lines if not (line.isspace() or line == "")]
    if len(lines) == 0 or len(content_lines) == 0:
        return css

    first_line = content_lines[0]
    first_line_without_indent = first_line.lstrip(" ")
    indent_size = len(first_line) - len(first_line_without_indent)
    if indent_size == 0:
        return css

    for i, line in enumerate(lines):
        if line.isspace() or line == "":
            continue

        indent = line[:indent_size]
        if not indent.isspace():
            return css  # Abort indent

        lines[i] = line[indent_size:]

    return "\n".join(lines)
