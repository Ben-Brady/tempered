from utils import setup_django, setup_jinja2, setup_tempered
import tempered
from data import user
import time
import timeit
import os
from pathlib import Path


def benchmark_render(
    name: str,
    entry_point: str,
    folder: str,
    context: dict = {},
):
    render_tempered = setup_tempered(f"{folder}/tempered", entry_point, context)
    render_jinja2 = setup_jinja2(f"{folder}/jinja", f"{entry_point}.html", context)
    render_django = setup_django(f"{folder}/django", f"{entry_point}.html", context)

    runs: dict[str, float] = {}

    def bench(name, func):
        duration = 2
        end = time.time() + duration

        renders = 0
        while time.time() < end:
            func()
            renders += 1

        per_second = int(renders / duration)
        print(f" {name:>10}: {per_second:,}/s")
        runs[name] = per_second

    print(name.title())
    bench("Tempered", render_tempered)
    bench("Jinja2", render_jinja2)
    bench("Django", render_django)


def benchmark_build():
    templates = tempered.Tempered("./building/tempered")
    start = time.perf_counter()

    count = 25
    duration = timeit.timeit(lambda: templates.build_memory(), number=count)
    duration /= count
    print(f"Tempered Building")
    print(f" {'tempered':>10}: {duration:2f}s")


os.chdir(Path(__file__).parent)
benchmark_build()
benchmark_render(
    name="Full Page Application",
    context={"user": user},
    entry_point="page",
    folder="./real_world",
)
benchmark_render(
    name="Partials",
    context={"profile": user},
    entry_point="page",
    folder="./partials",
)
benchmark_render(
    name="Static Pages",
    entry_point="page",
    folder="./static",
)
