#!/bin/bash

APP_NAME=${1:-app}
BACKEND_PORT=${2:-6066}
FRONTEND_PORT=${3:-6166}
FILE_PORT=${4:-6266}
HOSTNAME=${5:-9733n.lab}

echo "Building and running $APP_NAME with backend on port $BACKEND_PORT and frontend on port $FRONTEND_PORT..."

# Generate certificates for backend
mkdir -p backend/api/certs || {
  echo ">>> Failed to create directories for backend"; exit 1;
}
chmod 700 backend/api/certs || {
  echo ">>> Failed to set permissions on backend directories"; exit 1;
}

echo ">>> Generating certificate for $HOSTNAME..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout backend/api/certs/selfsigned.key \
  -out backend/api/certs/selfsigned.crt \
  -subj "/C=US/ST=State/L=City/O=MyCompany/OU=IT/CN=$HOSTNAME" || {
  echo ">>> Error generating certificate!"; exit 1;
}
chmod 600 backend/api/certs/selfsigned.key && chmod 644 backend/api/certs/selfsigned.crt || exit 1

# Run docker-compose with custom environment variables
BACKEND_PORT=$BACKEND_PORT FRONTEND_PORT=$FRONTEND_PORT HOSTNAME=$HOSTNAME docker compose up --build -d || {
  echo ">>> Failed to start $APP_NAME services."; exit 1;
}

echo "$APP_NAME is running with:"
echo "- Backend: http://localhost:$BACKEND_PORT"
echo "- Frontend: http://localhost:$FRONTEND_PORT"

echo ">>> Waiting for container to start...sleep 5 sec"
sleep 5

curl -X GET http://localhost:${BACKEND_PORT}/numbers/ --insecure \
  && echo ">>> API endpoint is reachable." \
  || { echo ">>> Error: API endpoint failed!"; exit 1; }

echo ">>> Serving certificate with IP check..."
cd backend/api/certs || { echo ">>> Failed to enter certs directory"; exit 1; }

python3 server.py
echo ">>> Certificate server stopped after serving the file."