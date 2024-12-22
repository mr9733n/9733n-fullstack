from app import app
from asgiref.wsgi import WsgiToAsgi

# Обернуть Flask-приложение в ASGI
asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
