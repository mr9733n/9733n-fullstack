FROM python:3-slim AS build-env

ENV PYTHONPATH=/backend

WORKDIR /backend

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./api ./api

CMD ["uvicorn", "api.main:app", "--host=0.0.0.0", "--port=8000"]
