from flask import Flask
from controllers.portal_controller import portal_bp

app = Flask(__name__)
app.secret_key = "student_management_group08_secret_key"

app.register_blueprint(portal_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
