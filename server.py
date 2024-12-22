import http.server
import socketserver
import threading

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