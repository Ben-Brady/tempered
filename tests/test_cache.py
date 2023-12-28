from . import build_template
import time
import pytest


@pytest.mark.skip("Cache removed temporarily")
def test_parse_runs_are_cached():
    template = "A {{a}}" * 500
    start = time.time()
    build_template(template)
    first_duration = time.time() - start

    start = time.time()
    build_template(template)
    secondary_duration = time.time() - start

    # The second parse should be much faster
    assert (first_duration / secondary_duration) > 1.5


@pytest.mark.skip("Cache removed temporarily")
def test_different_templates_arent_cached():
    template_a = "A {{a}}" * 200
    template_b = "A {{a}}" * 199
    start = time.time()
    build_template(template_a)
    first_duration = time.time() - start

    start = time.time()
    build_template(template_b)
    secondary_duration = time.time() - start

    # The second parse should be much faster
    assert (first_duration / secondary_duration) < 1.5
