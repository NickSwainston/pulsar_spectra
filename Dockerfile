FROM python:3.12

LABEL maintainer="Nick Swainston <nickswainston@gmail.com>"

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /uvx /bin/

# Work in a app build directory
WORKDIR /app
ADD pyproject.toml uv.lock src /app/

# Install pulsar_spectra using uv
RUN uv sync --frozen --extra bayesian

# Pin the psrqpy (and matplotlib) cache to a fixed path inside the image so
# the container works regardless of how HOME is set at runtime (e.g. when run
# as a non-root user or with -u).
ENV XDG_CACHE_HOME=/app/.cache
ENV MPLCONFIGDIR=/app/.config/matplotlib

# Download the ATNF catalogue so it is pre-cached in the image
RUN uv run python -c "from pulsar_spectra.catalogue import get_atnf_references; get_atnf_references()"

# Make the cache dirs world-readable/writable so any runtime user can use them
RUN mkdir -p /app/.cache /app/.config && chmod -R 777 /app/.cache /app/.config

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "--no-project", "python"]