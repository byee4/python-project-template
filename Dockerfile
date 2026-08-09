# Multi-stage build: build a wheel, then install it into a slim runtime image.
FROM python:3.12-slim AS build
WORKDIR /src
RUN pip install --no-cache-dir build
COPY . .
RUN python -m build --wheel --outdir /dist

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
COPY --from=build /dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl

# The console script installed by pyproject's [project.scripts] is the entry
# point. Args passed to `docker run <image> ...` go straight to the CLI.
ENTRYPOINT ["mytool"]
CMD ["--help"]
