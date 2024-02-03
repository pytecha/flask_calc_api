import numpy as np
import re

REG_FNS_AND_TEMPS = {
  "lin" : (lambda x, a, b: a + b*x, "$a+$b*x", "(y-$a)/$b"),
  "inv" : (lambda x, a, b: a + b/x, "$a+$b/x", "$b/(y-$a)"),
  "log" : (lambda x, a, b: a + b*np.log(x), "$a+$b*ln(x)", "e**((y-$a)/$b)"),
  "exp1": (lambda x, a, b: a*x**b, "$a*x**$b", "(y/$a)**(1/$b)"),
  "exp2": (lambda x, a, b: a*np.exp(b*x), "$a*e**($b*x)", "ln(y/$a)/$b"),
  "exp3": (lambda x, a, b: a*b**x, "$a*$b**x", "ln(y/$a)/ln($b)"),
  "quad": (
    lambda x, a, b, c: a + b*x +c*x**2,
    "$a+$b*x+$c*x**2", "quad($c,$b,$a-y)"
  )
}

TOKENS_ARG_POSITIONING = {
  '@acos': 'rg', '@acosh': 'rg', '@asin': 'rg',
  '@asinh': 'rg', '@atan': 'rg', '@atanh': 'rg',
  '@cbrt': 'rg', '@comb': 'bi', '@cos': 'rg',
  '@cosh': 'rg', '@deci': 'bi', '@deg': 'lf',
  '@exp': 'bi', '@fact': 'lf', '@frac': 'bi',
  '@grad': 'lf', '@ln': 'rg', '@log': 'rg',
  '@perc': 'lf', '@perm': 'bi', '@rad': 'lf',
  '@sin': 'rg', '@sinh': 'rg', '@sqrt': 'rg',
  '@tan': 'rg', '@tanh': 'rg', '@xpredf': 'lf',
  '@xroot': 'bi', '@ypredf': 'lf'
}

BP = re.compile("[\w\)][\*/@\+\-,]") # breakpoint re
LB = re.compile("(?<=[\*/\+\-,])\(") # match left brackets
RB = re.compile("\)(?=[\*/\+\-,])") #  match right brackets
VA = re.compile("[\s\+\-]*\.?[\w#@,\(\)\s]+") # validator re
DC = re.compile("^@deci") # @deci replacer
XY = re.compile("@\w(?!\w)") # @(x|y)pred replacer
ST = re.compile("=>[A-FMXY][\+\-]?$")
