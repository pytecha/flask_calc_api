from flask import Blueprint, request, jsonify
from .mathlab.functions import solver, deviation,\
  regression, to_frac, to_time, formater
from .mathlab.constants import REG_FNS_AND_TEMPS
from .mathlab.utils import Unit
from .auth import token_required

solutions = Blueprint("solutions", __name__)

keys = ("expression", "unit", "stats", "config")
get_body = lambda req: (req.json.get(key) for key in keys)

@solutions.route("/main", methods=["POST"])
# @token_required()
def main():
  expr, unit, stats, config = get_body(request)
  return jsonify({
    "solution": formater(solver(expr, Unit(unit), stats), config)
  })

@solutions.route("/deviation", methods=["POST"])
@token_required()
def std_deviation():
  expr, unit, stats, *_ = get_body(request)
  return jsonify({
    "solution": deviation(tuple(map(
      lambda _expr_: solver(_expr_, unit, stats),
      expr.split(",")
    )))
  })

@solutions.route("/regression", methods=["POST"])
@token_required()
def xy_regression():
  expr, unit, stats, *_ = get_body(request)
  kind = request.json.get("kind")
  x, y = [], []
  for item in expr.split(";"):
    i, j = item.split(",")
    x.append(i)
    y.append(j)
  _solver_ = lambda _expr_: solver(_expr_, unit, stats)
  return jsonify({
    "solution": regression(
      tuple(map(_solver_, x)),
      tuple(map(_solver_, y)),
      *REG_FNS_AND_TEMPS[kind]
    )
  })

@solutions.route("/conversion", methods=["POST"])
@token_required()
def conversion():
  kind = request.json.get("kind")
  expr = request.json.get("expression")
  dp = request.json.get("dp")
  return jsonify({
    "solution": (
      to_frac(expr) if kind == "frac" else\
      to_time(expr) if kind == "time" else\
      (
        res:=round(expr, dp),
        f"{res:,.15f}".rstrip("0").rstrip(".")
      ) if kind == "round" else\
      "".join((
        f"{expr*10**-dp:,.15f}".rstrip("0").rstrip("."),
        f"e{dp:0>2}")
      ) # -> kind == "eng"
    )
  })