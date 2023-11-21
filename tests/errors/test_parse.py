from tempered import Tempered
import pytest

INVALID_BLOCK_TEMPLATE = "tests/errors/templates/invalid_block.html"


@pytest.mark.skip
def test_invalid_end_block():
    Tempered().add_template(INVALID_BLOCK_TEMPLATE)
