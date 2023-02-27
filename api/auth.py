from flask import request, abort, current_app
from functools import wraps
from .models import User
import jwt

def token_required(roles=["basic"]):
  def outer(f):
    @wraps(f)
    def inner(*args, **kwargs):
      token = request.headers.get("X-API-TOKEN", None)
      if not roles or not token:
        abort(403)
      try:
        payload = jwt.decode(
          jwt=token,
          key=current_app.config["SECURITY_KEY"],
          algorithms=["HS256"],
          options={
            "require": ["sub"],
            "verify_signature": True
          }
        )
        user = User.query.filter_by(username=payload["sub"]).first()
        if not user: abort(401)
        user_roles = [item.role for item in user.roles]
        for role in roles:
          if role not in user_roles: abort(403)
      except Exception: abort(400)

      return f(*args, **kwargs)

    return inner

  return outer