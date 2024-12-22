FROM python:3.12.5-alpine

ENV PYTHONPATH=/frontend/src

WORKDIR /src

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /src

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
