import numpy as np
import math as mt
import statistics as stat
import functools
import json
import re
from random import random
from scipy.optimize import curve_fit
from string import Template as TP
from fractions import Fraction
from werkzeug.exceptions import InternalServerError
from .utils import AC, PolRec, Unit
from .exceptions import UnboundedArg, UnmatchedArg, EmptyArg, ExpressionError
from .constants import TOKENS_ARG_POSITIONING, BP, LB, RB, VA, DC, XY

def deviation(x):
  return {\
    "mean": stat.fmean(x), "pstd": stat.pstdev(x), "n": len(x),\
    "median": stat.median(x), "mode": stat.mode(x),\
    "std": stat.stdev(x) if len(x) > 1 else mt.nan\
  }

def regression(x, y, regf, ty, tx):
  x, y = np.array(x), np.array(y)
  popt, _ = curve_fit(regf, x, y, method="trf")
  coefr = np.corrcoef(y,regf(x, *popt))[0,1].item()
  popt = dict(zip(("a", "b", "c"), [i.item() for i in popt]))
  popt["c"] = popt.get("c", mt.nan)
  return {\
    **popt, "r": coefr, "xpreds": TP(tx).substitute(popt),\
    "ypreds": TP(ty).substitute(popt)\
  }

def xpredf(y, xpreds):
  return eval(xpreds.replace("y", str(y)), {"e": mt.e, "ln": mt.log, "quad": quad})

def ypredf(x, ypreds):
  return eval(ypreds.replace("x", str(x)), {"e": mt.e, "ln": mt.log})

def quad(a, b, c):
  d = mt.sqrt(b**2-4*a*c)
  x, y = (-b+d)/(2*a), (-b-d)/(2*a)
  return PolRec(x, y) if x != y else x

def pol_rec(inverse=False, basic=False):
  def decorator(func):
    @functools.wraps(func)
    def wrapper(*v):
      if len(v) < 2:
        def transf(x): return AC.aconvert(func(x)) if inverse else\
          func(AC.convert(x)) if basic else func(x)
        return PolRec(transf(x.x), transf(x.y)) if\
          isinstance(x:=v[0], PolRec) else transf(x)
      else:
        (x, y), is_pol_rec, _any_ = v, lambda x: isinstance(x, PolRec), False
        return PolRec(
          next(res:=map(
            lambda x: func(*x),
            ((x.x, y.x), (x.y, y.y)) if (_any_:=is_pol_rec(x) and is_pol_rec(y)) else\
            ((x.x, y), (x.y, y)) if (_any_:=is_pol_rec(x)) else ((y.x, x), (y.y, x))
          )),
          next(res)
        ) if _any_ or is_pol_rec(y) else func(x, y)
    return wrapper
  return decorator
 
@pol_rec(basic=True)
def sin(x):
  return mt.sin(x)

@pol_rec(inverse=True)
def asin(x):
  return mt.asin(x)

@pol_rec()
def sinh(x):
  return mt.sinh(x)

@pol_rec()
def asinh(x):
  return mt.asinh(x)

@pol_rec(basic=True)
def cos(x):
  return mt.cos(x)

@pol_rec(inverse=True)
def acos(x):
  return mt.acos(x)

@pol_rec()
def cosh(x):
  return mt.cosh(x)

@pol_rec()
def acosh(x):
  return mt.acosh(x)

@pol_rec(basic=True)
def tan(x):
  return mt.tan(x)

@pol_rec(inverse=True)
def atan(x):
  return mt.atan(x)

@pol_rec()
def tanh(x):
  return mt.tanh(x)

@pol_rec()
def atanh(x):
  return mt.atanh(x)

@pol_rec()
def deg(x):
  return AC.deg(x)
  
@pol_rec()
def grad(x):
  return AC.grad(x)
  
@pol_rec()
def rad(x):
  return AC.rad(x)
 
@pol_rec()  
def fact(x):
  return mt.factorial(int(x))

@pol_rec()
def ln(x):
  return mt.log(x)

@pol_rec()
def log(x):
  return mt.log10(x)

@pol_rec()
def sqrt(x):
  return mt.sqrt(x)

@pol_rec()
def cbrt(x):
  return mt.cbrt(x)

@pol_rec()
def xroot(x, y):
  return mt.pow(y, 1/x)
  
@pol_rec()
def exp(x, y):
  return mt.pow(x, y)
  
@pol_rec()
def comb(x, y):
  return mt.comb(int(x), int(y))

@pol_rec()
def perm(x, y):
  return mt.perm(int(x), int(y))
  
def perc(x):
  return x/100
  
def frac(a, b, c=None):
  return -(abs(a)+abs(b)/abs(c)) if c is not None and\
    any((a<0, b<0, c<0)) else a+b/c if c is not None else a/b

def deci(h, m=0, s=0):
  decimal = abs(m/60)+abs(s/3600)
  return -(abs(h)+decimal) if\
    any((h<0, m<0, s<0)) else h+decimal
  
def polar(x, y):
  return PolRec(
    mt.hypot(x, y),
    AC.aconvert(mt.atan2(y, x))
  )

def rect(radius, theta):
  return PolRec(
    radius*mt.cos(AC.convert(theta)),
    radius*mt.sin(AC.convert(theta))
  )

def to_frac(x, k):
  a, b = Fraction(x).limit_denominator().as_integer_ratio()
  if k == "p" and (c:=a // b) and 1 < b < a:
      return f"{c}/{a%b}/{b}"
  return str(a) if b == 1 else f"{a}/{b}"
  
def to_time(x):
  hrs = int(x:=float(x))
  mins = int(rem:=x%1*60)
  secs = int(rem:=rem%1*60)
  if (cns:=round(rem%1*100)) == 100:
    secs += 1
    cns = 0
  if secs == 60:
    mins += 1
    secs = 0
  if mins == 60:
    hrs += 1
    mins = 0
  sc = [secs, cns] if cns > 0 else [secs]
  return f"{hrs}⁰{mins}⁰{''.join([str(i) for i in sc])}"

def tokens_analyzer(expr, start=0):
  if (start:=expr.find("@", start)) != -1:
    expr_len, func_chars = len(expr), []
    while (index:=start+len(func_chars)+1) < expr_len and (c:=expr[index]).isalpha():
      func_chars.append(c)
    right = (init_right:=expr[slice(index, None)])
    
    try:
      arg1 = get_left_arg(expr, start - 1, -1)
    except ExpressionError as e:
      if e.__class__ is not EmptyArg:
        raise ExpressionError
        
    left = expr[slice(0, start-len(arg1:=locals().get("arg1", "")))]
    func = "".join(func_chars)
    
    if (pos:=TOKENS_ARG_POSITIONING[f"@{func}"]) == "lf":
      if not arg1:
        raise ExpressionError
      return tokens_analyzer(f"{left}{func}({arg1 + (''.join([',',func[0],'preds']) if 'predf' in func else '')}){right}", index)
    
    try:
      arg2 = get_right_arg(expr, index, expr_len)
      if func == "deci" and arg2[slice(0, 1)] in "+-":
        raise EmptyArg
    except ExpressionError as e:
      if func != "deci" and e.__class__ is EmptyArg:
        raise ExpressionError
        
    right = expr[slice(index+len(locals().get("arg2", "")), None)]
    
    if pos == "bi":
      if not arg1:
        raise ExpressionError
      if func in ("deci", "frac") and right.startswith(f"@{func}"):
        try:
          arg3 = get_right_arg(right, 5, len(right))
          if func == "deci" and arg3[slice(0, 1)] in "+-":
            raise EmptyArg
        except ExpressionError as e:
          if func != "deci" and e.__class__ is EmptyArg:
            raise ExpressionError
            
        if not DC.match(temp:=right[slice(5+len(locals().get("arg3", "")), None)])\
          and  func == "deci":
          expr = f"{left}{func}({arg1},{arg2}){DC.sub('', right)}"
        else:
          expr = f"{left}{func}({arg1},{arg2},{arg3}){DC.sub('', temp)}"
      elif func == "deci":
        expr = f"{left}{func}({arg1}){init_right}"
      else:
        expr = f"{left}{func}({arg1},{arg2}){right}"
      return tokens_analyzer(expr, index)
      
    elif pos == "rg":
      if arg1:
        arg1 = f'{arg1}*'
      return tokens_analyzer(f"{left}{arg1}{func}({arg2}){right}", start)
  else:
    return re.sub(
      "(#|\w#|[A-FMQXYde\)0-9]\()",
      lambda x: f"{m[0]}*" if (ew:=(m:=x.group(0))[slice(-1,-2,-1)] == "#")\
        and len(m) > 1 else "" if ew else f"{m[0]}*(",
      expr
    )

def validate_arg(func):
  @functools.wraps(func)
  def wrapper(*args):
    arg = func(*args)
    if not arg.strip():
      raise EmptyArg
    elif arg.count("(") != arg.count(")"):
      raise UnboundedArg
    elif VA.match(arg):
      return arg
    else:
      raise UnmatchedArg
  return wrapper
  
@validate_arg
def get_left_arg(expr, start, end):
  chars = []
  while start > end:
    char = expr[start]
    parens_eq = chars.count("(") == chars.count(")")
    last = "".join([char]+chars[slice(-1, -2, -1)])
    if (BP.match(last) or char == "(" or LB.match(last)) and parens_eq:
      if chars and chars[-1] in "*+-/," and char != "(":
        chars.pop()
      return "".join(reversed(chars))
    chars.append(char)
    start -= 1
  return "".join(reversed(chars))

@validate_arg
def get_right_arg(expr, start, end):
  chars = []
  while start < end:
    char = expr[start]
    parens_eq = chars.count("(")  == chars.count(")")
    last = "".join(chars[slice(-1, -2, -1)]+[char])
    if (BP.match(last) or char == ")" or RB.match(last)) and parens_eq:
      return "".join(chars)
    chars.append(char)
    start += 1
  return "".join(chars)

def formatter(x, config):
  dp = int(config["dp"])
  return (
    format(x, f",.{dp}f") if\
      config["dsp"] == "fix" else\
    format(x, f".{dp}e") if\
      config["dsp"] == "sci" else\
    " :: ".join(map(
      lambda a: a.rstrip("0").rstrip("."),
      format(x, ",.12f").split(" :: ")
    ))
  )

def get_body(req):
  expr, data, config = [req.json.get(key) for key in ("expr", "data", "config")]
  data = {k: v if "preds" in k else float(v) for k, v in data.items()}
  return expr, data, config

def request_error_handler(func):
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except (ArithmeticError, ValueError):
      return "Math Error", 500
    except (SyntaxError, TypeError):
      return "Syntax Error", 500
    except InternalServerError:
      return "Server Error", 500
  return wrapper

def solver(expr, data, config):
  AC.unit = Unit(config["unt"])
  return eval(
    tokens_analyzer(expr),
    {
      "acos": acos, "acosh": acosh, "asin": asin, "asinh": asinh,
      "atan": atan, "atanh": atanh, "cbrt": cbrt, "comb": comb,
      "cos": cos, "cosh": cosh, "deci": deci, "deg": deg, "d": 10, "e": mt.e,
      "exp": exp, "fact": fact, "frac": frac, "grad": grad,
      "ln": ln, "log": log, "nan": mt.nan, "perc": perc, "perm": perm, "pi": mt.pi,
      "polar": polar, "rad": rad, "rand": random(), "rect": rect, "sin": sin, 
      "sinh": sinh, "sqrt": sqrt, "tan": tan, "tanh": tanh, "xroot": xroot,
      "xpredf": xpredf, "ypredf": ypredf, **data
    }
  )