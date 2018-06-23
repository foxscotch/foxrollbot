class FoxRollBotException(Exception):
    pass

class InvalidSyntaxException(FoxRollBotException):
    pass

class NotANumberException(FoxRollBotException):
    pass

class OutOfRangeException(FoxRollBotException):
    pass

class TooManyPartsException(FoxRollBotException):
    pass