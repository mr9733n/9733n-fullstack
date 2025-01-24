FROM python:3.12.6-alpine

ENV PYTHONPATH=/backend

WORKDIR /backend

RUN apk add --no-cache \
    gcc \
    python3-dev \
    musl-dev \
    linux-headers \
    libffi-dev \
    build-base

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./api ./api

CMD ["uvicorn", "api.main:app", "--host=0.0.0.0", "--port=8000"]
