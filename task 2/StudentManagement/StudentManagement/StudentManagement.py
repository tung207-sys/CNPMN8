import threading
import webbrowser
from flask import Flask
from views.student_view import student_bp

app = Flask(__name__)
app.secret_key = "student_management_secret_key"
app.register_blueprint(student_bp)


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")


if __name__ == "__main__":
    # Tự động mở trình duyệt web sau 1 giây
    threading.Timer(1.0, open_browser).start()
    app.run(debug=False, port=5000)