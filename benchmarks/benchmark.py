from real_world import user
import timeit


def folder_benchmark(
    *,
    name: str,
    count: int,
    context: dict,
    entry_point: str,
    jinja_folder: str,
    django_folder: str,
    tempered_folder: str,
):
    # Setup jinja2
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader(jinja_folder))
    jinja_template = env.get_template(f"{entry_point}.html")
    jinja2 = lambda: jinja_template.render(**context)

    # Setup django
    from django.template.backends.django import DjangoTemplates
    import django
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_")
    django.setup()
    DJANGO_SETTINGS = {
        "NAME": "bench",
        "DIRS": [django_folder],
        "APP_DIRS": False,
        "OPTIONS": {},
    }
    django_templates = DjangoTemplates(DJANGO_SETTINGS)
    django_template = django_templates.get_template(f"{entry_point}.html")
    assert django_template
    django = lambda: django_template.render(context)

    # Setup Tempered
    from tempered import Tempered

    tempered_module = Tempered(tempered_folder).build_static()
    tempered_template = getattr(tempered_module, entry_point)
    tempered = lambda: tempered_template(**context)

    format = lambda time_taken: int(1 / (time_taken / count))
    print(name.title())
    django_ps = format(timeit.timeit(django, number=count))
    print(f"    Django: {django_ps:,}/s")
    jinja2_ps = format(timeit.timeit(jinja2, number=count))
    print(f"    Jinja2: {jinja2_ps:,}/s")
    tempered_ps = format(timeit.timeit(tempered, number=count))
    print(f"    Tempered: {tempered_ps:,}/s")


folder_benchmark(
    name="Real World Example",
    context={"user": user},
    count=10_000,
    entry_point="page",
    django_folder="./real_world/django",
    jinja_folder="./real_world/jinja",
    tempered_folder="./real_world/tempered",
)
