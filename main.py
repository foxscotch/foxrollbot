import re
import random
import logging

from telegram.ext import CommandHandler
from telegram.ext.updater import Updater


logging.basicConfig(filename='log.txt')

with open('token.txt') as token_file:
    token = token_file.read().strip()


class InvalidSyntaxException(Exception):
    pass

class NotANumberException(Exception):
    pass

class OutOfRangeException(Exception):
    pass


class DiceRoll:
    syntax_regex = re.compile('(\d{1,3})d(\d{1,4})')

    def __init__(self, qty, die):
        self.qty = qty
        self.die = die

    @staticmethod
    def from_str(roll_str):
        match = re.match(DiceRoll.syntax_regex, roll_str)
        if match:
            try:
                qty = int(match.group(1))
                die = int(match.group(2))

                if qty < 1 or qty > 100:
                    raise OutOfRangeException('Number of dice must be between 1 and 100.')
                if die < 1 or die > 1000:
                    raise OutOfRangeException('Number of sides must be between 1 and 1000.')

                return DiceRoll(qty, die)
            except ValueError as e:
                # I can't imagine this will ever happen, because the regex
                # should prevent any non-numbers. But, you know, just in case.
                raise NotANumberException('Both the number of dice and number of sides must be numbers.')
        else:
            raise InvalidSyntaxException()

    def roll(self):
        results = []
        for i in range(self.qty):
            results.append(random.randint(1, self.die))
        return RollResult(self.qty, self.die, results)

    def __str__(self):
        return '{0}d{1}'.format(self.qty, self.die)


class RollResult:
    def __init__(self, qty, die, results):
        self.qty = qty
        self.die = die
        self.results = results

    def __str__(self):
        return '{0}d{1}: | {2}'.format(self.qty, self.die, ', '.join(self.results))


class CompleteRoll:
    syntax_regex = re.compile('(\d{1,3}d\d{1,4})(\+(\d{1,3}d\d{1,4}|\d{1,3}))*')

    def __init__(self, rolls):
        pass

    @staticmethod
    def from_args(self, arg_list):
        if len(args) >= 3 or len(args) == 0:
            raise InvalidSyntaxException('Improper number of arguments.')

        adv = 0
        if len(arg_list) == 2:
            if 'advantage'.startswith(arg_list[1]):
                adv = 1
            elif 'disadvantage'.startswith(arg_list[1]):
                adv = -1
            else:
                raise InvalidSyntaxException('Invalid advantage argument.')

    def roll(self):
        pass


class CompleteRollResult:
    def __init__(self, rolls, total, modifiers, mod_total):
        self.rolls = rolls
        self.total = total
        self.modifiers = modifiers
        self.mod_total = mod_total

    def __str__(self):
        total = 'Total: {0}\n'.format(self.total)
        roll_results = ''
        for roll in self.rolls:
            roll_results += str(roll) + '\n'


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
        pass
    except InvalidSyntaxException as e:
        msg_args['text'] = 'Syntax: /roll <rolls>d<die>+[roll/modifier]+[etc] [dis/adv]'
    except (NotANumberException, OutOfRangeException) as e:
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
