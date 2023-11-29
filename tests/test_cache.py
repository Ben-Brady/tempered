from utils import build_template
import time


def test_parse_runs_are_cached():
    start = time.time()
    build_template("{{ a }}" * 2)
    first_duration = time.time() - start

    start = time.time()
    build_template("{{ a }}" * 2)
    secondary_duration = time.time() - start

    # The second parse should be much faster
    assert secondary_duration < (first_duration / 2)
