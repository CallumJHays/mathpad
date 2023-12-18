
docs:
	cd docs && \
		poetry run jupyter-book build .

serve-docs:
	cd docs/_build && \
		poetry run python -m http.server 8000

.PHONY: docs serve-docs
