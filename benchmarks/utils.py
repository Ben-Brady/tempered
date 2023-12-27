from typing import Callable
import os


try:
    import django as _, jinja2 as _, tempered as _
except (ModuleNotFoundError, ImportError) as e:
    print("Benchmark packages not installed, run `pip install tempered jinja2 django`")
    raise e

def setup_django(folder: str, template: str, context: dict) -> Callable[[], str]:
    from django.template.backends.django import DjangoTemplates
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_")
    django.setup()
    DJANGO_SETTINGS = {
        "NAME": "bench",
        "DIRS": [folder],
        "APP_DIRS": False,
        "OPTIONS": {},
    }
    django_templates = DjangoTemplates(DJANGO_SETTINGS)
    django_template = django_templates.get_template(template)
    assert django_template
    return lambda: django_template.render(context)


def setup_jinja2(folder: str, template: str, context: dict) -> Callable[[], str]:
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader(folder))
    jinja_template = env.get_template(template)
    return lambda: jinja_template.render(**context)


def setup_tempered(folder: str, template: str, context: dict) -> Callable[[], str]:
    from tempered import Tempered
    tempered_module = Tempered(folder).build_static()
    tempered_template = getattr(tempered_module, template)

    return lambda: tempered_template(**context)
