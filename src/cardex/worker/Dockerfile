FROM python:3.12

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
      uv sync --frozen --no-install-project
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
	uv sync --frozen

CMD ["uv", "run", "python", "-m", "cardex.worker"]
