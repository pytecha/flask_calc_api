from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from dotenv import dotenv_values
from flask_cors import CORS

db = SQLAlchemy()
ma = Marshmallow()

config = dotenv_values("/home/pytecha/flask_calc_api/.env")

def init_app():
  app = Flask("calculator-api")
  CORS(app, resources={r"/api/solutions/*": {"origins": ["http://localhost:3000", "https://pytecha.pythonanywhere.com"]}})

  app.config["SECURITY_KEY"] = config["SECURITY_KEY"]
  app.config["SQLALCHEMY_DATABASE_URI"] = config["DB_URI"]
  app.config["SQLALCHEMY_POOL_RECYCLE"] = 300
  app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
  app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True

  db.init_app(app)
  ma.init_app(app)

  from .users import users
  from .solutions import solutions
  app.register_blueprint(users, url_prefix="/api/users")
  app.register_blueprint(solutions, url_prefix="/api/solutions")

  from .models import User, ReqHist
  with app.app_context():
    db.create_all()
  return app
