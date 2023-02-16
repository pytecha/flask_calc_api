from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

db = SQLAlchemy()
ma = Marshmallow()

def init_app():
  app = Flask("calculator-api")
  CORS(app)
  app.config["SECURITY_KEY"] = "flaskcalculatorwebapp" # need change
  app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://pytecha:xftgvcxc@pytecha.mysql.pythonanywhere-services.com/pytecha$codec"
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
