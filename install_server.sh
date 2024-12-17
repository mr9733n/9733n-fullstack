#!/bin/bash
echo "Running as $(whoami)"

HOSTNAME=${1:-get-sms-free.lab}
API_PORT=6066
FILE_PORT=6166
APP_NAME=get-sms-free-api

mkdir -p certs config logs || { echo ">>> Failed to create directories"; exit 1; }
chmod 700 certs config logs || { echo ">>> Failed to set permissions on directories"; exit 1; }

echo ">>> Generating certificate for ${HOSTNAME}..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout certs/selfsigned.key \
    -out certs/selfsigned.crt \
    -subj "/C=US/ST=State/L=City/O=MyCompany/OU=IT/CN=${HOSTNAME}" || { echo ">>> Error generating certificate!"; exit 1; }

chmod 600 certs/selfsigned.key && chmod 644 certs/selfsigned.crt || exit 1

EXISTING_CONTAINER=$(docker ps -aq -f name=${APP_NAME})
if [ ! -z "$EXISTING_CONTAINER" ]; then
  echo ">>> Stopping and removing existing container..."
  docker stop ${APP_NAME} && docker rm -f ${APP_NAME}
fi

EXISTING_IMAGE=$(docker images -q ${APP_NAME})
if [ ! -z "$EXISTING_IMAGE" ]; then
  echo ">>> Removing existing Docker image..."
  docker rmi -f ${APP_NAME}
fi

echo ">>> Cooking Docker image..."
docker build -t ${APP_NAME} --build-arg HOSTNAME=${HOSTNAME} . || { echo ">>> Error building Docker image!"; exit 1; }

echo ">>> Running Docker container..."
docker run -d --restart always --name ${APP_NAME} -p ${API_PORT}:8000 -e HOSTNAME=${HOSTNAME} ${APP_NAME} \
  && echo ">>> Server is running at https://${HOSTNAME}:${API_PORT}" \
  || { echo ">>> Error running Docker container!"; exit 1; }

echo ">>> Waiting for container to start...sleep 5 sec"
sleep 5

curl -X GET https://localhost:${API_PORT}/numbers/countries --insecure \
  && echo ">>> API endpoint is reachable." \
  || { echo ">>> Error: API endpoint failed!"; exit 1; }

echo ">>> Serving certificate with IP check..."
cd certs || { echo ">>> Failed to enter certs directory"; exit 1; }

python3 - <<EOF
import http.server
import socketserver
import threading

ALLOWED_IP = "192.168.0.50"
PORT = 6166
HOST = "192.168.0.100"

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
