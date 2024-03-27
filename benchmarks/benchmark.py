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
    runs: dict[str, float] = {}

    def bench(name, func):
        duration = 2
        end = time.time() + duration

        renders = 0
        while time.time() < end:
            func()
            renders += 1

        per_second = int(renders / duration)
        per_second_str = f"{per_second:,}/s"

        ms_per_render = 1000 / per_second
        print(f" {name:>10}: {per_second_str:>10} | {ms_per_render:.3f}ms ")
        runs[name] = per_second

    print(name.title())

    render_tempered = setup_tempered(f"{folder}/tempered", entry_point, context)
    bench("Tempered", render_tempered)

    render_jinja2 = setup_jinja2(f"{folder}/jinja", entry_point, context)
    bench("Jinja2", render_jinja2)

    render_django = setup_django(f"{folder}/django", entry_point, context)
    bench("Django", render_django)


def benchmark_build():
    start = time.perf_counter()
    TARGET_DURATION = 5
    target_end = start + TARGET_DURATION

    compiles = 0
    while time.perf_counter() < target_end:
        tempered.Tempered(template_folder="./building/tempered")
        compiles += 1

    end = time.perf_counter()
    duration = (end - start) / compiles
    print(f"Tempered Building: {duration:2f}s")


os.chdir(Path(__file__).parent)
benchmark_build()
benchmark_render(
    name="Full Page Application",
    context={"user": user},
    entry_point="page.html",
    folder="./real_world",
)
benchmark_render(
    name="Partials",
    context={"profile": user},
    entry_point="page.html",
    folder="./partials",
)
benchmark_render(
    name="Static Pages",
    entry_point="page.html",
    folder="./static",
)
