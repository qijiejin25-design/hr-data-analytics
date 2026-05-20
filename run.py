"""开发模式启动入口。生产环境建议使用 gunicorn 等 WSGI 服务器。"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
