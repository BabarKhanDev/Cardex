FROM python:3.12

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project   # deps only
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen 
ENV FLASK_APP=cardex.web

EXPOSE 8080
CMD ["flask", "run", "-p", "8080", "--host", "0.0.0.0"]
