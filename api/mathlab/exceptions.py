class UnmatchedArg(Exception):
  def __init__(self, msg="unmatched arguments"):
    super().__init__(msg)
    
class EmptyArg(Exception):
  def __init__(self, msg="argument required"):
    super().__init__(msg)

class MissingBound(Exception):
  def __init__(self, msg="unable to locate boundary"):
    super().__init__(msg)
    
class ExpressionError(Exception):
  def __init__(self, msg="syntax error in expression"):
    super().__init__(msg)
    