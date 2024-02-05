ruff check tempered/ tests/ --fix
autoflake --in-place -r tempered/ tests/
isort --profile black tempered/ tests/
black tempered/ tests/
