import enum
import math as mt

class Unit(enum.Enum):
  DEG = "deg"
  GRAD = "grad"
  RAD = "rad"

class AC(object):
  # angle unit convertor
  unit = Unit.DEG
  
  @staticmethod
  def convert(x):
    # for cosine, sine & tangent methods
    unit = AC.unit
    return mt.radians(x) if unit is Unit.DEG else\
      x*mt.pi/200 if unit is Unit.GRAD else x

  @staticmethod
  def aconvert(x):
    # for arccosine, arcsine & arctangent methods
    unit = AC.unit
    return mt.degrees(x) if unit is Unit.DEG else\
      mt.degrees(x)/0.9 if unit is Unit.GRAD else x
  
  @staticmethod
  def deg(x):
    unit = AC.unit
    return x/0.9 if unit is Unit.GRAD else\
      mt.radians(x) if unit is Unit.RAD else x
  
  @staticmethod
  def grad(x):
    unit = AC.unit
    return x*0.9 if unit is Unit.DEG else\
      x*mt.pi/200 if unit is Unit.RAD else x
  
  @staticmethod
  def rad(x):
    unit = AC.unit
    return x*200/mt.pi if unit is Unit.GRAD else\
      mt.degrees(x) if unit is Unit.DEG else x
    
class PolRec(object):
  def __init__(self, x=0, y=0):
      self.x = x
      self.y = y

  def __str__(self):
    return f"{self.x} :: {self.y}"

  def __format__(self, val):
    return f"{self.x:{val}} :: {self.y:{val}}"
    
  def __abs__(self):
    return PolRec(abs(self.x), abs(self.y))
    
  def __round__(self, dp=0):
    return PolRec(round(self.x, dp), round(self.y, dp))
    
  def __pos__(self):
    return PolRec(self.x, self.y)
    
  def __neg__(self):
    return PolRec(-self.x, -self.y)

  def compute(self, other, op, side="l"):
    if isinstance(other, PolRec):
      if side == "r":
        x, y = eval(f"({other.x}{op}{self.x},{other.y}{op}{self.y})")
      else:
        x, y = eval(f"({self.x}{op}{other.x},{self.y}{op}{other.y})")
    else:
      if side == "r":
        x, y = eval(f"({other}{op}{self.x},{other}{op}{self.y})")
      else:
        x, y = eval(f"({self.x}{op}{other},{self.y}{op}{other})")
    if op in ("==", "!=", ">", ">=", "<", "<="):
      return x and y
    return PolRec(x,y)

  def __eq__(self,other):
    return self.compute(other,"==")

  def __ne__(self,other):
    return self.compute(other,"!=")

  def __gt__(self,other):
    return self.compute(other,">")

  def __ge__(self,other):
    return self.compute(other,">=")

  def __lt__(self,other):
    return self.compute(other,"<")

  def __le__(self,other):
    return self.compute(other,"<=")

  def __add__(self,other):
    return self.compute(other,"+")
  
  def __radd__(self,other):
    return self.compute(other,"+","r")

  def __sub__(self,other):
    return self.compute(other,"-")

  def __rsub__(self,other):
    return self.compute(other,"-","r")

  def __mul__(self,other):
    return self.compute(other,"*")

  def __rmul__(self,other):
    return self.compute(other,"*","r")

  def __truediv__(self,other):
    return self.compute(other,"/")

  def __rtruediv__(self,other):
    return self.compute(other,"/","r")

  def __floordiv__(self,other):
    return self.compute(other,"//")

  def __rfloordiv__(self,other):
    return self.compute(other,"//","r")
  
  def __mod__(self,other):
    return self.compute(other,"%")

  def __rmod__(self,other):
    return self.compute(other,"%","r")
  
  def __pow__(self,other):
    return self.compute(other,"**")

  def __rpow__(self,other):
    return self.compute(other,"**","r")
