import pytest
import tempered
from tests import build_template, build_templates


def test_checks_detect_missing_layout():
    with pytest.raises(tempered.InvalidTemplateException):
        build_template('''
        <script type="tempered/metadata">
        layout: missing
        </script>
        ''')


def test_checks_detect_invalid_layout():
    with pytest.raises(tempered.InvalidTemplateException):
        build_templates(
            '''
            <script type="tempered/metadata">
            layout: non_layout
            </script>
            ''',
            ("non_layout", "This isn't a layout"),
        )


@pytest.mark.skip
def test_checks_detect_missing_components():
    with pytest.raises(tempered.InvalidTemplateException):
        build_template('<t:Invalid()></t:Invalid()>')


def test_checks_detect_invalid_blocks():
    with pytest.raises(tempered.InvalidTemplateException):
        build_templates(
            """
            <script type"tempered/metadata">
            layout: layout
            </script>

            <t:block name="nonexist">
                This is invalid
            </block>
            """,
            ("layout", "<t:slot name='exists'></t:slot>"),
        )


def test_checks_detect_missing_blocks():
    with pytest.raises(tempered.InvalidTemplateException):
        build_templates(
            """
            <script type"tempered/metadata">
            layout: layout
            </script>

            <t:block name="nonexist">
                This is invalid
            </block>
            """,
            ("layout", "<t:slot name='mandatory' required></t:slot>"),
        )
