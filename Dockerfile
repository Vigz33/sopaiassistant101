# syntax=docker/dockerfile:1
FROM python:3.12.1-alpine3.19
RUN addgroup --gid 2000 appuser && \
  adduser --disabled-password --no-create-home --uid 1000 --ingroup appuser appuser

WORKDIR /app
COPY --link app /app
COPY --link app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt -q

USER 1000

# COPY --link app /app
ENTRYPOINT ["python", "/app/main.py"]