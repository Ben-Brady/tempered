import sys
from tempered import __version__
from .parser.parse_ast import Template
import tempfile
import pickle
import ast
from pathlib import Path
from hashlib import sha256


TMP_DIR = Path(tempfile.gettempdir(), "tempered-cache")
TMP_DIR.mkdir(parents=True, exist_ok=True)

_version = sys.version_info
PYTHON_VERSION = f"{_version.major}.{_version.minor}.{_version.micro}"
use_cache = True


def disable_cache():
    global use_cache
    use_cache = False


def clear_cache():
    for file in TMP_DIR.iterdir():
        if file.is_file():
            file.unlink(missing_ok=True)


def generate_cache_path(type: str, hash: str) -> Path:
    cache_key = f"tempered_{type}-{PYTHON_VERSION}-{__version__}:{hash}"
    cache_file = Path(TMP_DIR, f"{cache_key}")
    return cache_file


def get_parse_cache(html: str) -> Template | None:
    hash = _generate_parse_hash(html)
    cache_file = generate_cache_path("template", hash)
    if not cache_file.exists():
        return None

    with open(cache_file, "rb") as f:
        template = pickle.load(f)

    if not isinstance(template, Template):
        cache_file.unlink()
        return None

    return template


def set_parse_cache(html: str, template: Template):
    hash = _generate_parse_hash(html)
    cache_file = generate_cache_path("template", hash)

    with open(cache_file, "wb") as f:
        pickle.dump(template, f)

    return None


def _generate_parse_hash(html: str) -> str:
    return sha256(html.encode()).hexdigest()
