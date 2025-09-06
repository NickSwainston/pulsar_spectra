FROM python:3.12

LABEL maintainer="Nick Swainston <nickswainston@gmail.com>"

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /uvx /bin/


# Work in a app build directory
WORKDIR /app
ADD pyproject.toml uv.lock src /app

# Install pulsar_spectra using uv
RUN uv sync --frozen

# Download the ATNF references so they're cached in the image
RUN uv run python -c "from pulsar_spectra.catalogue import get_atnf_references; get_atnf_references()"

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "--no-project", "python"]