import strictyaml
from strictyaml import Str, Map, Optional, MapPattern, Seq
import bs4
from dataclasses import dataclass, field
import typing_extensions as t
import warnings
import textwrap
from ..errors import ParsingWarning


@dataclass
class Metadata:
    parameters: t.Dict[str, str] = field(default_factory=dict)
    style_includes: t.List[str] = field(default_factory=list)
    imports: t.Dict[str, str] = field(default_factory=dict)
    layout: t.Union[str, None] = None


def extract_metadata_from_soup(soup: bs4.BeautifulSoup) -> Metadata:
    metadataScript = soup.find("script", {"type": "tempered/metadata"})
    if not isinstance(metadataScript, bs4.Tag):
        return Metadata()

    yaml = metadataScript.text
    metadataScript.decompose()

    yaml = yaml.strip("\n")
    yaml = textwrap.dedent(yaml)

    try:
        metadata = parse_metadata_yaml(yaml)
        return metadata
    except Exception:
        err = ParsingWarning("Invalid template metadata, falling back to default")
        warnings.warn(err)
        raise
        return Metadata()


def parse_metadata_yaml(text: str) -> Metadata:
    schema = Map({
        Optional("layout"): Str(),
        Optional("style_includes"): Seq(Str()),
        Optional("imports"): MapPattern(Str(), Str()),
        Optional("parameters"): MapPattern(Str(), Str()),
    })
    data = strictyaml.load(text, schema).data
    assert isinstance(data, dict) or data is None

    if data is None:
        return Metadata()

    return Metadata(
        imports=data.get("imports", {}),
        parameters=data.get("parameters", {}),
        style_includes=data.get("style_includes", []),
        layout=data.get("layout", None)
    )


# <script type="tempered/metadata">
# layout: layout.html
# parameters:
#     foo: str
#     bar: str
# imports:
#     Foo: foo.html
#     Bar: bar.html
# style_includes:
#     - foo.html
#     - bar.html
# </script>
