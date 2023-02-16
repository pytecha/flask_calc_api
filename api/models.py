from werkzeug.security import generate_password_hash
from sqlalchemy.sql import func
from . import db, ma

class User(db.Model):
  __tablename__ = "users"
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(32), unique=True, index=True)
  email = db.Column(db.String(128), unique=True)
  password = db.Column(db.String(256))
  token = db.Column(db.String(256))
  tk_date = db.Column(db.DateTime(timezone=True), default=func.now())
  role = db.relationship("Role")
  errlog = db.relationship("ErrLog")
  reqhist = db.relationship("ReqHist")
  
  def hash_password(self):
    self.password = generate_password_hash(self.password, method="sha256")

class ReqHist(db.Model):
  __tablename__ = "req_hists"
  id = db.Column(db.Integer, primary_key=True)
  expression = db.Column(db.String(10240))
  solution = db.Column(db.String(256))
  req_date = db.Column(db.DateTime(timezone=True), default=func.now())
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

class ErrLog(db.Model):
  __tablename__ = "err_logs"
  id = db.Column(db.Integer, primary_key=True)
  expression = db.Column(db.String(10240))
  err_log = db.Column(db.String(256))
  err_date = db.Column(db.DateTime(timezone=True), default=func.now())
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

class Role(db.Model):
  __tablename__ = "roles"
  id = db.Column(db.Integer, primary_key=True)
  role = db.Column(db.String(32))
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

class RoleSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = Role
    include_fk = True

class ErrLogSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = ErrLog
    include_fk = True

class ReqHistSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = ReqHist
    include_fk = True
    
class UserSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = User
  role = ma.List(ma.Nested(RoleSchema))
  errlog = ma.List(ma.Nested(ErrLogSchema))
  reqhist = ma.List(ma.HyperlinkRelated("users.req_hist_detail"))
