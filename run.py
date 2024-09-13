import webbrowser
import threading
from app import create_app
import os


def open_browser():
    if not webbrowser._tryorder:  # Check if the browser hasn't been opened already
        webbrowser.open_new("http://127.0.0.1:5000/")


if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.25, open_browser).start()
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
