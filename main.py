import re
import random
import logging

from telegram.ext import CommandHandler
from telegram.ext.updater import Updater


logging.basicConfig(filename='log.txt')

with open('token.txt') as token_file:
    token = token_file.read().strip()


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


class DiceRoll:
    syntax_regex = re.compile('[+-]?(\d+)d(\d+)')

    def __init__(self, qty, die, negative=False):
        self.qty = qty
        self.die = die
        self.negative = negative

    @staticmethod
    def from_str(roll_str):
        if roll_str.startswith('+') or roll_str.startswith('-'):
            sign, roll_str = roll_str[0], roll_str[1:]
        else:
            sign = '+'

        match = DiceRoll.syntax_regex.fullmatch(roll_str)

        if match:
            try:
                qty = int(match.group(1))
                die = int(match.group(2))

                if qty < 1 or qty > 100:
                    raise OutOfRangeException('Number of dice must be between 1 and 100.')
                if die < 1 or die > 1000:
                    raise OutOfRangeException('Number of sides must be between 1 and 1000.')

                return DiceRoll(qty, die, sign == '-')
            except ValueError as e:
                # I can't imagine this will ever happen, because the regex
                # should prevent any non-numbers. But, you know, just in case.
                raise NotANumberException('Both the number of dice and number of sides must be numbers.')
        else:
            raise InvalidSyntaxException('Invalid syntax')

    def roll(self):
        results = []
        for i in range(self.qty):
            results.append(random.randint(1, self.die))
        return RollResult(self.qty, self.die, results, self.negative)

    def __str__(self):
        return '{0}d{1}'.format(self.qty, self.die)


class RollResult:
    def __init__(self, qty, die, results, negative):
        self.qty = qty
        self.die = die
        self.results = results
        self.negative = negative

    def __str__(self):
        return '{0}d{1}: {2} | {3}'.format(self.qty, self.die, sum(self.results), ', '.join(map(lambda x: str(x), self.results)))


class CompleteRoll:
    syntax_regex = re.compile('(\d+d\d+)([+-](\d+d\d+|\d+))*')

    def __init__(self, rolls, modifiers):
        self.rolls = rolls
        self.modifiers = modifiers

    @staticmethod
    def from_args(args):
        if len(args) >= 3 or len(args) == 0:
            raise InvalidSyntaxException('Improper number of arguments.')

        adv = 0
        if len(args) == 2:
            if 'advantage'.startswith(args[1]):
                adv = 1
            elif 'disadvantage'.startswith(args[1]):
                adv = -1
            else:
                raise InvalidSyntaxException('Invalid advantage argument.')

        if CompleteRoll.syntax_regex.fullmatch(args[0]):
            parts = re.split('[+-](?=[+-])', re.sub('([+-])', '\g<1>\g<1>', args[0]))
            rolls = []
            modifiers = []

            if len(parts) > 25:
                raise TooManyPartsException('A roll may only have up to 25 parts.')

            for part in parts:
                match = DiceRoll.syntax_regex.match(part)
                if match:
                    rolls.append(DiceRoll.from_str(part))
                else:
                    num = int(part)
                    if num > 1000:
                        raise OutOfRangeException('Modifiers must be between 1 and 1000.')
                    else:
                        modifiers.append(int(part))

            return CompleteRoll(rolls, modifiers)
        else:
            raise InvalidSyntaxException('Invalid syntax')

    def roll(self):
        results = []
        for roll in self.rolls:
            results.append(roll.roll())
        return CompleteRollResult(results, self.modifiers)


class CompleteRollResult:
    def __init__(self, rolls, modifiers):
        self.rolls = rolls
        self.roll_total = sum([-sum(roll.results) if roll.negative else sum(roll.results) for roll in rolls])
        self.modifiers = modifiers
        self.mod_total = sum(modifiers)
        self.total = self.roll_total + self.mod_total

    def __str__(self):
        total = 'Total: {0}\n'.format(self.total)
        roll_results = '\n'.join(map(lambda x: str(x), self.rolls)) + '\n'
        mod_total = 'Modifier total: {0}'.format(self.mod_total)
        return total + roll_results + mod_total


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
        text="Hi! This is a dice-rolling bot created by @AndroFox and " +
             "@foxscotch, since @RollGramBot has suddenly become unreliable.")


def roll(bot, update, args):
    msg_args = {
        'chat_id': update.message.chat_id,
        'reply_to_message_id': update.message.message_id
    }

    try:
        roll = CompleteRoll.from_args(args)
        msg_args['text'] = str(roll.roll())
    except InvalidSyntaxException as e:
        msg_args['text'] = 'Syntax: /roll <rolls>d<die>+[roll/modifier]+[etc] [dis/adv]'
    except FoxRollBotException as e:
        msg_args['text'] = str(e)

    bot.send_message(**msg_args)


if __name__ == '__main__':
    updater = Updater(token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('roll', roll, pass_args=True))

    #updater.start_webhook('127.0.0.1', 6969, token,
    #    webhook_url='https://bot.foxscotch.us/' + token)
    updater.start_polling()
