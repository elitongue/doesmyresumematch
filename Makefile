.PHONY: fmt fmt-check migrate test
fmt:
	pre-commit run --all-files

fmt-check:
	pre-commit run --all-files --show-diff-on-failure

migrate:
	alembic -c apps/api/alembic.ini upgrade head

test:
	pytest
