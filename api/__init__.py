from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from dotenv import load_dotenv
from flask_cors import CORS
import os

db = SQLAlchemy()
ma = Marshmallow()

def init_app():
  app = Flask("calculator-api")
  CORS(app)
  load_dotenv()
  app.config["SECURITY_KEY"] = os.getenv("SECURITY_KEY")
  app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI")
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
