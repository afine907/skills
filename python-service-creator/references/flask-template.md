# Flask Template

## App Factory

```python
from flask import Flask
from flask_cors import CORS

from app.core.config import settings
from app.api.users import users_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings)

    CORS(app)

    app.register_blueprint(users_bp, url_prefix="/api/v1/users")

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app
```

## 路由模式 (Blueprint)

```python
from flask import Blueprint, request, jsonify

users_bp = Blueprint("users", __name__)


@users_bp.route("/", methods=["GET"])
def list_users():
    return jsonify([])


@users_bp.route("/<user_id>", methods=["GET"])
def get_user(user_id):
    return jsonify({"id": user_id})


@users_bp.route("/", methods=["POST"])
def create_user():
    data = request.get_json()
    return jsonify({"id": "1", **data}), 201
```

## 配置

```python
from os import environ

class Config:
    SECRET_KEY = environ.get("SECRET_KEY", "dev")
    DATABASE_URI = environ.get("DATABASE_URI", "sqlite:///app.db")
    DEBUG = environ.get("DEBUG", "false").lower() == "true"
```

## 启动

```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
```
