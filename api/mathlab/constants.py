from string import Template as TP
import re, numpy as np

REG_FNS_AND_TEMPS = {
  "lin" : (lambda x, a, b: a + b*x, TP("$a+$b*@x"), TP("(@y-$a)/$b")),
  "inv" : (lambda x, a, b: a + b/x, TP("$a+$b/@x"), TP("$b/(@y-$a)")),
  "log" : (lambda x, a, b: a + b*np.log(x), TP("$+$b*ln(@x)"), TP("e**((@y-$a)/$b)")),
  "exp1" : (lambda x, a, b: a*x**b, TP("$a*@x**$b"), TP("(@y/$a)**(1/$b)")),
  "exp2": (lambda x, a, b: a*np.exp(b*x), TP("$a*e**($b*@x)"), TP("ln(@y/$a)/$b")),
  "exp3": (lambda x, a, b: a*b**x, TP("$a*$b**@x"), TP("ln(@y/$a)/ln($b)")),
  "quad": (lambda x, a, b, c: a + b*x +c*x**2, TP("$a+$b*@x+$c*@x**2"), TP("quad($c,$b,$a-@y)"))
}

TOKENS_ARG_POSITIONING = {
  '@A': 'lf-const', '@Ans': 'lf-const',
  '@B': 'lf-const', '@C': 'lf-const', '@D': 'lf-const',
  '@E': 'lf-const', '@F': 'lf-const', '@M': 'lf-const',
  '@X': 'lf-const', '@Y': 'lf-const', '@a': 'lf-const',
  '@acos': 'bi-const', '@acosh': 'bi-const', '@asin': 'bi-const',
  '@asinh': 'bi-const', '@atan': 'bi-const', '@atanh': 'bi-const',
  '@b': 'lf-const', '@c': 'lf-const', '@cbrt': 'bi-const',
  '@comb': 'bi', '@cos': 'bi-const', '@cosh': 'bi-const',
  '@deci': 'lf', '@deg': 'lf', '@e': 'lf-const', '@expt': 'bi',
  '@fact': 'lf', '@frac': 'lf', '@grad': 'lf', '@ln': 'bi-const',
  '@log': 'bi-const', '@meanx': 'lf-const', '@meany': 'lf-const',
  '@n': 'lf-const', '@perc': 'lf', '@perm': 'bi', '@pi': 'lf-const',
  '@polar': 'lf-const', '@powex': 'bi-const', '@powtx': 'bi-const',
  '@pstdx': 'lf-const', '@pstdy': 'lf-const', '@r': 'lf-const',
  '@rad': 'lf', '@rand': 'lf-const', '@rect': 'lf-const',
  '@sin': 'bi-const', '@sinh': 'bi-const', '@sqrt': 'bi-const',
  '@stdx': 'lf-const', '@stdy': 'lf-const', '@sumfrx': 'lf-const',
  '@sumtrx': 'lf-const', '@sumtwx': 'lf-const', '@sumtwxy': 'lf-const',
  '@sumtwy': 'lf-const', '@sumx': 'lf-const', '@sumxy': 'lf-const',
  '@sumy': 'lf-const', '@tan': 'bi-const', '@tanh': 'bi-const',
  '@xpred': 'lf', '@xroot': 'bi', '@ypred': 'lf'
}

RE = re.compile("@[a-zA-Z]+") # token re
MA = re.compile("(deci\(|frac\()+") # deci|frac re
BP = re.compile("[\w\)][\*/\+\-,]") # breakpoint re
LB = re.compile("(?<=[\*/\+\-,])\(") # match left brackets
RB = re.compile("\)(?=[\*/\+\-,])") #  match right brackets
VA = re.compile("[\s\+\-]*\.?[\w@,\(\)\s]+") # validator re
XY = re.compile("@\w(?!\w)") # @(x|y)pred replacer