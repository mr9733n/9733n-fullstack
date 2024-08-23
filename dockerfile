FROM python:3.12.5-alpine

RUN apk add --no-cache bash && \
    adduser -D -s /bin/bash myuser

WORKDIR /app

COPY --chown=root:root app/ /app/app/
COPY --chown=root:root config/ /app/config/
COPY --chown=root:root logs/ /app/logs/
COPY --chown=root:myuser certs/ /app/certs/

RUN chmod 700 /app/certs && chmod 600 /app/certs/*

RUN pip install --no-cache-dir -r /app/app/requirements.txt

USER myuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile", "/app/certs/selfsigned.key", "--ssl-certfile", "/app/certs/selfsigned.crt"]
