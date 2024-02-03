from flask import Flask
from flask_cors import CORS

def init_app():
  app = Flask("calculator-api")
  
  CORS(app, resources={r"/api/solutions/*": {"origins": ["http://localhost:3000", "http://localhost:8000", "https://pytecha.pythonanywhere.com"]}})

  app.config["SECURITY_KEY"] = "flaskcalculatorwebapp"
  
  from .solutions import solutions
  app.register_blueprint(solutions, url_prefix="/api/solutions")

  return app
