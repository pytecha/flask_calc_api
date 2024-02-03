
class ExpressionError(Exception):
  def __init__(self, msg="invalid expression, check entry sequences"):
    super().__init__(msg)

class UnmatchedArg(ExpressionError):
  def __init__(self, msg="arguments not matching"):
    super().__init__(msg)

class EmptyArg(ExpressionError):
  def __init__(self, msg="argument is required"):
    super().__init__(msg)

class UnboundedArg(ExpressionError):
  def __init__(self, msg="argument bound overflow"):
    super().__init__(msg)

