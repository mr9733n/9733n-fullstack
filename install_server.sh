#!/bin/bash

HOSTNAME=${1:-get-sms-free.lab}

mkdir -p certs config logs

echo ">>> Generating certificate for ${HOSTNAME}..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout certs/selfsigned.key \
    -out certs/selfsigned.crt \
    -subj "/C=US/ST=State/L=City/O=MyCompany/OU=IT/CN=${HOSTNAME}"

if [ $? -ne 0 ]; then
  echo ">>> Error generating certificate!"
  exit 1
fi

EXISTING_CONTAINER=$(docker ps -q -f name=get-sms-free-api)
if [ ! -z "$EXISTING_CONTAINER" ]; then
  echo ">>> Stopping and removing existing container..."
  docker stop get-sms-free-api
  docker rm get-sms-free-api
fi

echo ">>> Cooking Docker image..."
docker build -t get-sms-free-api --build-arg HOSTNAME=${HOSTNAME} .

if [ $? -ne 0 ]; then
  echo ">>> Error building Docker image!"
  exit 1
fi

echo ">>> Running Docker container..."
docker run -d --name get-sms-free-api -p 8000:8000 -e HOSTNAME=${HOSTNAME} get-sms-free-api

if [ $? -eq 0 ]; then
  echo ">>> Server is running at https://${HOSTNAME}:8000"
else
  echo ">>> Error running Docker container!"
  exit 1
fi