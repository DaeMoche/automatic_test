class AssertTypeError(Exception):
    """
    断言类型错误异常
    """

    def __init__(self, msg: str = "未定义的断言方式") -> None:
        self.message = msg
        super().__init__(self.message)


class ParamsIsEmptyError(Exception):

    def __init__(self, msg: str = "参数不能为空") -> None:
        self.message = msg
        super().__init__(self.message)


class CustomError(Exception):
    """
    自定义错误异常
    """

    def __init__(self, msg: str = "自定义异常") -> None:
        self.message = msg
        super().__init__(self.message)
