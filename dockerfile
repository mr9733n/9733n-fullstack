FROM python:3.12.5-alpine

RUN apk add --no-cache bash && \
    adduser -D -s /bin/bash myuser

WORKDIR /app

COPY --chown=root:root app/ /app/
COPY --chown=root:root app/config/ /app/config/
COPY --chown=root:root app/logs/ /app/logs/
COPY --chown=root:root app/static/ /app/static/
COPY --chown=root:root app/templates/ /app/templates/
COPY --chown=myuser:myuser app/certs/ /app/certs/
COPY --chown=root:root requirements.txt /app/app/requirements.txt

RUN chmod 700 /app/certs && \
    chmod 644 /app/certs/selfsigned.crt && \
    chmod 600 /app/certs/selfsigned.key && \
    chown myuser:myuser /app/certs/selfsigned.key /app/certs/selfsigned.crt

RUN chown -R myuser:myuser /app/logs
RUN chmod 755 /app/logs

RUN pip install --no-cache-dir -r /app/requirements.txt

USER myuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile", "/app/certs/selfsigned.key", "--ssl-certfile", "/app/certs/selfsigned.crt"]
