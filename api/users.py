from flask import Blueprint, abort, request, current_app
from sqlalchemy import desc
from . import db
from .auth import token_required
from .models import User, UserSchema,\
  ReqHist, ReqHistSchema, Role
import jwt

users = Blueprint("users", __name__)

user_schema = UserSchema()
users_schema = UserSchema(many=True)
req_hist_schema = ReqHistSchema()
req_hists_schema = ReqHistSchema(many=True)

keys = ("username", "email", "password")
get_body = lambda req: (req.json.get(key) for key in keys)
gen_token = lambda username: jwt.encode(
  payload={"sub": username},
  key=current_app.config["SECURITY_KEY"]
)

@users.route("/all", methods=["GET"])
@token_required()
def users_list():
  return users_schema.dump(User.query.all())

@users.route("/create", methods=["POST"])
# @token_required()
def create_user():
  if None in (data:=tuple(get_body(request))):
    abort(400)
  user = User.query.filter_by(username=data[0]).first()
  if user: abort(400)
  try:
    user = User(
      username=data[0],
      email=data[1],
      password=data[2],
      token=gen_token(data[0])
    )
  except Exception as e:
    abort(500, description=str(e))
  user.hash_password()
  role = Role(role="basic")
  user.role.append(role)
  db.session.add(user)
  db.session.add(role)
  db.session.commit()
  return (user_schema.dump(user), 201)

@users.route("/req-hists", methods=["GET"])
@token_required()
def users_req_hists_list():
  return req_hists_schema.dump(
    ReqHist.query.order_by(desc(ReqHist.req_date)).all()
  )

@users.route("/req-hists/<int:id>", methods=["GET", "DELETE"])
@token_required()
def req_hist_detail(id):
  req_hist = ReqHist.query.get_or_404(id)
  if request.method == "GET":
    return req_hist_schema.dump(req_hist)
  else:
    db.session.delete(req_hist)
    db.session.commit()
    return ("", 204)

@users.route("/<int:id>", methods=["GET", "PUT", "DELETE"])
@token_required()
def user_detail(id):
  user = User.query.get_or_404(id)
  if request.method == "GET":
    return user_schema.dump(user)
  elif request.method == "PUT":
    for key, value in zip(keys, get_body(request)):
      if value is not None and key != "username":
        setattr(user, key, value)
    db.session.commit()
    return user_schema.dump(user)
  else: # DELETE
    db.session.delete(user)
    db.session.commit()
    return ("", 204)

@users.route("/<int:id>/req-hists", methods=["GET"])
@token_required()
def user_req_hists_list(id):
  return req_hists_schema.dump(
    ReqHist.query.filter_by(user_id=id)
    .order_by(desc(ReqHist.req_date)).all()
  )
