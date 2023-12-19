from real_world import user
import timeit

def assert_imports():
    try:
        import django as _
    except:
        print("Django not installed, run `pip install django`")
        exit()

    try:
        import jinja2 as _
    except:
        print("Jinja2 not installed, run `pip install jinja2`")
        exit()

    try:
        import tempered as _
    except:
        print("Tempered not installed, run `pip install tempered`")
        exit()


def benchmark(
    *,
    name: str,
    count: int,
    context: dict,
    entry_point: str,
    folder: str,
):
    # Setup jinja2
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader(f"{folder}/jinja"))
    jinja_template = env.get_template(f"{entry_point}.html")
    render_jinja2 = lambda: jinja_template.render(**context)

    # Setup django
    from django.template.backends.django import DjangoTemplates
    import django
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_")
    django.setup()
    DJANGO_SETTINGS = {
        "NAME": "bench",
        "DIRS": [f"{folder}/django"],
        "APP_DIRS": False,
        "OPTIONS": {},
    }
    django_templates = DjangoTemplates(DJANGO_SETTINGS)
    django_template = django_templates.get_template(f"{entry_point}.html")
    assert django_template
    render_django = lambda: django_template.render(context)

    # Setup Tempered
    from tempered import Tempered

    tempered_module = Tempered(f"{folder}/tempered").build_static()
    tempered_template = getattr(tempered_module, entry_point)
    render_tempered = lambda: tempered_template(**context)

    def bench(name, func):
        time = timeit.timeit(func, number=count)
        per_second = int(1 / (time / count))
        print(f" {name:>10}: {time:>5.2f}s {per_second:,}/s")

    print(f"{name.title()} ({count:,}x)")
    bench("Tempered", render_tempered)
    bench("Jinja2", render_jinja2)
    bench("Django", render_django)


assert_imports()
benchmark(
    name="Full Page Application",
    context={"user": user},
    count=10_000,
    entry_point="page",
    folder="./real_world",
)
benchmark(
    name="Partials",
    context={"profile": user},
    count=250_000,
    entry_point="page",
    folder="./partials",
)
benchmark(
    name="Static Pages",
    context={},
    count=250_000,
    entry_point="page",
    folder="./static",
)
