FROM python:3.11-bookworm AS builder

RUN pip install -U pip setuptools wheel
RUN pip install pdm

COPY pyproject.toml pdm.lock README.md /app/

WORKDIR /app
RUN mkdir __pypackages__
RUN pdm sync --prod --no-editable


FROM python:3.11-bookworm

ENV PYTHONPATH=/app/pkgs
COPY --from=builder /app/__pypackages__/3.11/lib /app/pkgs

COPY --from=builder /app/__pypackages__/3.11/bin/* /bin/

WORKDIR /app
COPY src /app/src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
