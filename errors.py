class FoxRollBotException(Exception):
    pass


class InvalidSyntaxException(FoxRollBotException):
    pass


class NotANumberException(FoxRollBotException):
    pass


class NotEnoughArgumentsException(FoxRollBotException):
    pass


class OutOfRangeException(FoxRollBotException):
    pass


class TooManyComponentsException(FoxRollBotException):
    pass

class DoesNotExistException(FoxRollBotException):
    pass
