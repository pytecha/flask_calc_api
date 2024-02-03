from flask import Blueprint, request, jsonify
from itertools import chain
from .mathlab.functions import solver, deviation, regression, to_frac, to_time, formatter, get_body, request_error_handler
from .mathlab.constants import REG_FNS_AND_TEMPS, ST
from .mathlab.utils import Unit, PolRec

solutions = Blueprint("solutions", __name__)

@solutions.route("/main", methods=["POST"])
@request_error_handler
def main():
  expr, data, config = get_body(request)
  new_data = {"data": data}
  result_list = []
  for expr in expr.split(":"):
    app_var = ""
    if (match:=ST.search(expr)):
      app_var = match.group()[2:]
      expr = ST.sub("", expr, 1)
    result_list.append(result:=solver(expr, new_data["data"], config))
    if app_var in ("M+", "M-"):
      new_data["data"].update({"M": str(res:=eval(f'{data.get("M", "0")}{app_var[-1]}{result}'))})
      new_data.update({"Q": str(res), "Qf": formatter(res, config)})
      return jsonify(new_data)
    elif app_var:
      new_data["data"].update({app_var: str(result)})
  new_data.update({"Q": str(res.x if isinstance(res:=result_list[-1], PolRec) else res), "Qf": " ::: ".join([formatter(x, config) for x in result_list])})
  return jsonify(new_data)

@solutions.route("/deviation", methods=["POST"])
@request_error_handler
def std_deviation():
  expr, data, config = get_body(request)
  x_axis = tuple(map(
    lambda __expr: solver(__expr, data, config),
    chain(*[i.split(",") for i in expr.split(";")])
  ))
  return jsonify({"data": {key: str(value) for key, value in deviation(x_axis).items()}})
  
@solutions.route("/regression", methods=["POST"])
@request_error_handler
def xy_regression():
  expr, data, config = get_body(request)
  reg_kind = config["reg"]
  coords = ([], [])
  for (index, __expr) in enumerate(chain(*[i.split(",") for i in expr.split(";")])):
    coords[index%2].append(solver(__expr, data, config))
  data = {key: str(value) for (key, value) in regression(*coords, *REG_FNS_AND_TEMPS[reg_kind]).items()}
  return jsonify({"data": data})
  
@solutions.route("/trans-num", methods=["POST"])
@request_error_handler
def conversion():
  expr, _, config = get_body(request)
  result = {}
  if config["kind"].endswith("frac"):
    result["Qf"] = to_frac(expr, config["kind"][0])
  elif config["kind"] == "time":
    result["Qf"] = to_time(expr)
  elif config["kind"] == "round":
    result["Q"] = str(q:=round(float(expr), int(config["dp"])))
    result["Qf"] = formatter(q, config)
  elif config["kind"] == "eng":
    result["Qf"] = "".join((
      f'{float(expr)*10**-config["dp"]:,.15f}'.rstrip("0").rstrip("."),
      f'e{config["dp"]:0>2}')
    )
  else: # kind -> fmt
    result["Qf"] = formatter(float(expr), config)
  return jsonify(result)
