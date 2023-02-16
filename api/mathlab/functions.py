import numpy as np, math as mt, cmath
from random import random as rand
from scipy.optimize import curve_fit
from fractions import Fraction
from .utils import AC, PolRec, Unit
from .exceptions import *
from .constants import *

def deviation(x, q="x", in_reg=False):
  if not in_reg:
    x = np.array(x)
  return {
    key: value.item() for key, value in {
      f"sumtw{q}": np.sum(x**2), f"sum{q}": np.sum(x),
      f"mean{q}": np.mean(x), f"pstd{q}": np.std(x),
      f"std{q}": np.std(x, ddof=1) if len(x) > 1 else np.nan,
      "n": np.int32(x.size)
    }
    .items()
  }

def regression(x, y, regf, ty, tx):
  x, y = np.array(x), np.array(y)
  popt, _ = curve_fit(regf, x, y, method="trf")
  coefr = np.corrcoef(y,regf(x, *popt))[0,1].item()
  popt = dict(zip(("a", "b", "c"), [i.item() for i in popt]))
  return {
    **popt, "r":coefr, **deviation(x, in_reg=True),
    **deviation(y, "y", True), "sumxy": np.sum(x*y).item(),
    "sumtrx": np.sum(x**3).item(), "sumtwxy": np.sum(x**2*y).item(),
    "sumfrx": np.sum(x**4).item(), "xpred": f"@xpred({tx.substitute(popt)})",
    "ypred": f"@ypred({ty.substitute(popt)})"
  }

def quad(a, b, c):
  d = cmath.sqrt(b**2-4*a*c)
  d = d.real if d.imag == 0 else d
  return PolRec((-b+d)/(2*a), (-b-d)/(2*a))

def wrapper(func):
  def inner(x, y, *z):
    result = func(x, y)
    for i in z:
      result = func(result, i)
    return result
  return inner

@wrapper
def expt(x, y, *z):
  return x**y
  
@wrapper
def comb(x, y, *z):
  return mt.comb(x, y)

@wrapper
def perm(x, y, *z):
  return mt.perm(x, y)

def pol_rec(inverse=False, basic=False):
  # basic -> for trigonometric basic functions
  # inverse -> for inverse of trig functions
  def outer(func):
    def inner(x):
      if isinstance(x, PolRec):
        if inverse:
          return PolRec(AC.aconvert(func(x.x)),\
            AC.aconvert(func(x.y)))
        elif basic:
          return PolRec(func(AC.convert(x.x)),\
            func(AC.convert(x.y)))
        return PolRec(func(x.x), func(x.y))
      else:
        if inverse:
          return AC.aconvert(func(x))
        elif basic:
          return func(AC.convert(x))
        return func(x)
    return inner
  return outer
 
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
  return mt.factorial(x)

@pol_rec()
def ln(x):
  return mt.log(x)

@pol_rec()
def log(x):
  return mt.log10(x)

@pol_rec()
def to_frac(x):
  f = Fraction(x).limit_denominator()
  if (a:=f.numerator) > (b:=f.denominator):
    return f"{a//b}/{a%b}/{b}"
  return f"{a}/{b}"
  
def to_time(x):
  hrs = int(x)
  rem =  x%1*60
  mins = int(rem)
  rem = rem%1*60
  secs = int(rem)
  if (cns:=round(rem%1*100)) == 100:
    secs += 1; cns = 0
  if secs == 60:
    mins += 1; secs = 0
  if mins == 60:
    hrs += 1; mins = 0
  return f"{hrs}:{mins}:{secs}:{cns}"

def sqrt(x):
  return x**(1/2)

def cbrt(x):
  return x**(1/3)

def xroot(x, y, *z):
  result = y**(1/x)
  for i in z:
    result = i**(1/result)
  return result

def perc(x):
  return x/100
  
def powtx(x):
  return 10**x
  
def powex(x):
  return mt.e**x
  
def frac(a, b, c=None):
  return -(abs(a)+b/c) if c and a < 0 else\
    a+b/c if c else a/b

def deci(h, m=0, s=0, c=0):
  decimal = abs(m/60)+abs(s/3600)+abs(c/360000)
  return -(abs(h)+decimal) if h < 0 else h+decimal
  
def polar(x, y):
  radius = mt.hypot(x,y)
  theta = AC.aconvert(mt.atan2(y, x))
  return PolRec(radius, theta)  

def rect(radius, theta):
  x = radius*mt.cos(AC.convert(theta))
  y = radius*mt.sin(AC.convert(theta))
  return PolRec(x, y)

def tokens_analyzer(expression):
  if match:=RE.search(expression):
    matched = match.group(0)
    direction = TOKENS_ARG_POSITIONING[matched]
    errors = ("empty", "nomatch", "nobound")
    try:
      arg1 = get_left_arg(expression, match.start() - 1, -1)
    except EmptyArg:
      arg1 = errors[0]
    except UnmatchedArg:
      arg1 = errors[1]
    except MissingBound:
      arg1 = errors[2]
    end = 0 if arg1 in errors[:2] else len(arg1)
    left = expression[slice(0, match.start()-end)]
    right = expression[slice(match.end(), None)]
    func = matched.lstrip("@")
  
    if direction == "lf":
      if arg1 in errors: raise ExpressionError
      if func in ("xpred", "ypred"):
        right = XY.sub(arg1, right, count=1)
        return tokens_analyzer(f"{left}{right}")
      return tokens_analyzer(f"{left}{func}({arg1}){right}")
    
    elif direction == "lf-const":
      if arg1 in errors[2]: raise ExpressionError
      func = f"{func}()" if func == "rand" else func
      arg1 = '' if arg1 in errors[:2] else f'{arg1}*'
      return tokens_analyzer(f"{left}{arg1}{func}{right}")
    
    try:
      arg2 = get_right_arg(expression, match.end(), match.endpos)
    except (EmptyArg, UnmatchedArg, MissingBound):
      raise ExpressionError
    right = expression[slice(match.end()+len(arg2), None)]
    
    if direction == "bi":
      if arg1 in errors: raise ExpressionError
      if func == "frac":
        try:
          arg3 = get_right_arg(right, 0, len(right))
        except  (EmptyArg, UnmatchedArg, MissingBound): arg3 = "empty"
        if arg3 != "empty":
          right = right[slice(len(arg3), None)]
          return tokens_analyzer(f"{left}{func}({arg1},{arg2}, {arg3}){right}")
      return tokens_analyzer(f"{left}{func}({arg1},{arg2}){right}")
    
    elif direction == "bi-const":
      if arg1 in errors[2]: raise ExpressionError
      arg1 = '' if arg1 in errors[:2] else f'{arg1}*'
      return tokens_analyzer(f"{left}{arg1}{func}({arg2}){right}")
  else:
    expression = get_multi_args(expression, "deci", DC)
    replacer = lambda x: "" if (match:=x.group(0)) in "#" else f"{match[0]}*("
    return re.sub(r"(((?<!\w)\w\()|([0-9]+\()|(\)\()|#)", replacer, expression)

def validate_arg(func):
  def inner(*args):
    arg = func(*args)
    if not arg.strip(): raise EmptyArg
    elif arg.count("(") != arg.count(")"):
      raise MissingBound
    elif VA.match(arg): return arg
    else: raise UnmatchedArg
  return inner
  
@validate_arg
def get_left_arg(expression, start, end):
  chars = []
  while start > end:
    char = expression[start]
    parens_eq = chars.count("(") == chars.count(")")
    last = "".join([char]+chars[slice(-1, -2, -1)])
    if (BP.match(last) or char == "(" or LB.match(last)) and parens_eq:
      if chars and chars[-1] in "*+-/," and char != "(": chars.pop()
      return "".join(reversed(chars))
    chars.append(char)
    start -= 1
  return "".join(reversed(chars))

@validate_arg
def get_right_arg(expression, start, end):
  chars = []
  while start < end:
    char = expression[start]
    parens_eq = chars.count("(")  == chars.count(")")
    last = "".join(chars[slice(-1, -2, -1)]+[char])
    if (BP.match(last) or char == ")" or RB.match(last)) and parens_eq:
      return "".join(chars)
    chars.append(char)
    start += 1
  return "".join(chars)

def get_multi_args(expression, target, regex):
  if match:=regex.search(expression):
    start, end = match.span()
    args, chars, num = [], [], (end - start)//5
    while num > 0 and end < match.endpos:
      char = expression[end]
      parens_eq = chars.count("(") == chars.count(")")
      last = "".join(chars[slice(-1, -2, -1)]+[char])
      if (char == ")" or RB.match(last)) and parens_eq:
        args.append("".join(chars)); chars.clear()
        num -= 1; end += 1
        continue
      chars.append(char); end += 1
    argc = len(args)
    if ((argc < 2 or argc > 3) and target in "frac") or\
      (argc < 1 or argc > 4): raise Exception("unmatched args")
    left = expression[slice(0, start)]
    right = expression[slice(end, None)]
    expression = f'{left}{target}#({",".join(args)}){right}'
    return get_multi_args(expression, target, regex)
  else:
    return expression

def formater(x, config):
  formated = ""
  if config["disp"] == "fix":
    formated = format(x, f",.{config['dp']}f")
  elif config["disp"] == "sci":
    formated = format(x, f".{config['dp']}e")
  else: # disp -> nrm
    specs = {1: (",.", "f"), 2: (".", "e")}
    fs1, fs2 = specs[config["dp"]] # format specs
    formated = format(x, f"{fs1}15{fs2}").split(" :: ")
    for index, item in enumerate(formated):
      if config["dp"] == 2:
        item, sub = item.split("e")
        item = f'{item.rstrip("0").rstrip(".")}e{sub}'
      else:
        item = item.rstrip("0").rstrip(".")
      if item in "-0": item = "0"
      formated[index] = item
    formated = " :: ".join(formated)
  if isinstance(x, PolRec): x = x.x
  return (x, formated)

def solver(expression, unit=Unit.DEG, stats={}):
  AC.unit = unit
  return eval(
    tokens_analyzer(expression),
    {
      "acos": acos, "acosh": acosh, "asin": asin, "asinh": asinh,
      "atan": atan, "atanh": atanh, "cbrt": cbrt, "comb": comb,
      "cos": cos, "cosh": cosh, "deci": deci, "deg": deg, "e": mt.e,
      "expt": expt, "fact": fact, "frac": frac, "grad": grad,
      "ln": ln, "log": log, "nan": mt.nan, "perc": perc, "perm": perm, "pi": mt.pi,
      "polar": polar, "powex": powex, "powtx": powtx, "quad": quad,
      "rad": rad, "rand": rand, "rect": rect, "sin": sin, "sinh": sinh,
      "sqrt": sqrt, "tan": tan, "tanh": tanh, "xroot": xroot, **stats
    }
  )
  