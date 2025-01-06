import textwrap
from dataclasses import dataclass, field
import bs4
import strictyaml
from strictyaml import Any, Map, MapPattern, Optional, Seq, Str
import typing_extensions as t
from ..errors import ParserException


class ParameterObject(t.TypedDict):
    type: t.Optional[str]
    default: t.Optional[str]


@dataclass
class Metadata:
    parameters: t.Dict[str, t.Union[str, ParameterObject]] = field(default_factory=dict)
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
    except Exception as e:
        err = ParserException("Invalid template metadata")
        raise err from e


def parse_metadata_yaml(text: str) -> Metadata:
    schema = Map(
        {
            Optional("layout"): Str(),
            Optional("style_includes"): Seq(Str()),
            Optional("imports"): MapPattern(Str(), Str()),
            Optional("parameters"): MapPattern(Str(), Any()),
        }
    )
    data = strictyaml.load(text, schema).data
    assert isinstance(data, dict) or data is None

    if data is None:
        return Metadata()

    parameters: t.Dict[str, t.Union[str, ParameterObject]] = {}
    for key, value in data.get("parameters", {}).items():
        if isinstance(value, str):
            parameters[key] = value
        elif isinstance(value, dict):
            parameters[key] = {
                "default": value.get("default", None),
                "type": value.get("type", None),
            }

    return Metadata(
        imports=data.get("imports", {}),
        parameters=parameters,
        style_includes=data.get("style_includes", []),
        layout=data.get("layout", None),
    )
