#!/bin/bash

APP_NAME=${1:-app}
BACKEND_PORT=${2:-6066}
FRONTEND_PORT=${3:-6166}
FILE_PORT=${4:-6266}
HOSTNAME=${5:-9733n.lab}

# Получаем IP-адрес системы
BACKEND_IP=$(hostname -I | awk '{print $1}')

# Проверяем, что IP получен
if [ -z "$BACKEND_IP" ]; then
  echo ">>> Unable to determine system IP address. Exiting."
  exit 1
fi

# Путь до .env файла
ENV_FILE="frontend/src/.env"

# Создаем или обновляем .env файл
echo "API_HOST=http://${BACKEND_IP}:${BACKEND_PORT}" > $ENV_FILE
echo "GENERATE_NAME_ROUTE=/rna/generate/names" >> $ENV_FILE
echo "FLASK_SECRET_KEY=$(openssl rand -hex 16)" >> $ENV_FILE
echo "APP_VERSION=0.1.4.2" >> $ENV_FILE
echo "RSS_FEED_URL=https://www.newsru.co.il/il/www/news/hot" >> $ENV_FILE

echo ">>> .env file updated at $ENV_FILE:"
cat $ENV_FILE

echo "Building and running $APP_NAME with backend on port $BACKEND_PORT and frontend on port $FRONTEND_PORT..."

# Generate certificates for backend
mkdir -p backend/api/certs backend/api/logs || {
  echo ">>> Failed to create directories for backend"; exit 1;
}
chmod 700 backend/api/certs backend/api/logs || {
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
echo "- Backend: http://$BACKEND_IP:$BACKEND_PORT"
echo "- Frontend: http://$BACKEND_IP:$FRONTEND_PORT"

echo ">>> Waiting for container to start...sleep 5 sec"
sleep 5

curl -X GET http://$BACKEND_IP:${BACKEND_PORT}/numbers/ --insecure \
  && echo ">>> API endpoint is reachable." \
  || { echo ">>> Error: API endpoint failed!"; exit 1; }

curl -X GET http://$BACKEND_IP:${FRONTEND_PORT}/ --insecure \
  && echo ">>> API endpoint is reachable." \
  || { echo ">>> Error: API endpoint failed!"; exit 1; }

echo ">>> Serving certificate with IP check..."
cd backend/api/certs || { echo ">>> Failed to enter certs directory"; exit 1; }

python3 - <<EOF
import http.server
import socketserver
import threading

# TODO: Fix this
ALLOWED_IP = "192.168.0.50"
PORT = 6266
HOST = "0.0.0.0"

class IPCheckRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        client_ip = self.client_address[0]
        print(f">>> Received request from {client_ip}")

        if client_ip == ALLOWED_IP and self.path == "/selfsigned.crt":
            super().do_GET()
            print(f">>> File served to {ALLOWED_IP}. Shutting down the server.")
            threading.Thread(target=self.server.shutdown).start()
        else:
            print(f">>> Unauthorized access attempt from {client_ip}.")
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"403 Forbidden: Access Denied")

with socketserver.TCPServer((HOST, PORT), IPCheckRequestHandler) as httpd:
    print(f">>> Serving certificate at http://{HOST}:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n>>> Server manually stopped.")
EOF
echo ">>> Certificate server stopped after serving the file."