from utils import setup_django, setup_jinja2, setup_tempered
from data import user
import timeit
import os
from pathlib import Path
import matplotlib.pyplot as plt


def benchmark_render(
    name: str,
    count: int,
    entry_point: str,
    folder: str,
    context: dict = {},
):
    render_tempered = setup_tempered(f"{folder}/tempered", entry_point, context)
    render_jinja2 = setup_jinja2(f"{folder}/jinja", f"{entry_point}.html", context)
    render_django = setup_django(f"{folder}/django", f"{entry_point}.html", context)

    runs: dict[str, float] = {}

    def bench(name, func):
        time = timeit.timeit(func, number=count)
        per_second = int(1 / (time / count))
        print(f" {name:>10}: {time:>5.2f}s {per_second:,}/s")
        runs[name] = per_second

    print(f"{name.title()} ({count:,}x)")
    bench("Tempered", render_tempered)
    bench("Jinja2", render_jinja2)
    bench("Django", render_django)

    OUTPUT_DIR = Path("./output")
    OUTPUT_DIR.mkdir(exist_ok=True)
    plt.style.use("Solarize_Light2")
    plt.figure(figsize=(5, 5))
    plt.bar(
        x=list(runs.keys()),
        height=list(runs.values()),
    )
    plt.title(f"{name.title()} ({count:,}x)")
    plt.ylabel("Renders Per Second")
    filename = name.replace(" ", "-").lower() + ".png"
    plt.savefig(OUTPUT_DIR / filename)


os.chdir(Path(__file__).parent)
benchmark_render(
    name="Full Page Application",
    context={"user": user},
    count=50_000,
    entry_point="page",
    folder="./real_world",
)
benchmark_render(
    name="Partials",
    context={"profile": user},
    count=1_000_000,
    entry_point="page",
    folder="./partials",
)
benchmark_render(
    name="Static Pages",
    count=1_000_000,
    entry_point="page",
    folder="./static",
)
