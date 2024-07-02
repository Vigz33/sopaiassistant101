# syntax=docker/dockerfile:1
FROM python:3.12.1-alpine3.19
RUN addgroup --gid 2000 app && \
  adduser --disabled-password --no-create-home --uid 1000 --ingroup app app

COPY --link requirements.txt /opt/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /opt/requirements.txt -q

USER 1000

COPY --link app /opt/app

ENTRYPOINT ["python", "/opt/app/main.py"]
