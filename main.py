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


class RollCommandHandler(CommandHandler):
    """
    Small modification of telegram.ext.CommandHandler, with better splitting.
    """

    def handle_update(self, update, dispatcher):
        optional_args = self.collect_optional_args(dispatcher)

        if self.pass_args:
            optional_args['args'] = re.split('\s+', update.message.text)[1:]

        self.callback(dispatcher.bot, update, **optional_args)


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
            raise InvalidSyntaxException()

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
        if len(self.results) == 1:
            return '{0}d{1}: {2}'.format(self.qty, self.die, sum(self.results))
        else:
            return '{0}d{1}: {2} | {3}'.format(self.qty, self.die, sum(self.results), ', '.join(map(lambda x: str(x), self.results)))


class CompleteRoll:
    syntax_regex = re.compile('(\d+d\d+|\d+)([+-](\d+d\d+|\d+))*')

    def __init__(self, rolls, modifiers):
        self.rolls = rolls
        self.modifiers = modifiers

    @staticmethod
    def from_str(roll_str):
        if CompleteRoll.syntax_regex.fullmatch(roll_str):
            parts = re.split('[+-](?=[+-])', re.sub('([+-])', '\g<1>\g<1>', roll_str))
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

            if len(rolls) == 0:
                raise InvalidSyntaxException()

            return CompleteRoll(rolls, modifiers)
        else:
            raise InvalidSyntaxException()

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

        if len(self.modifiers) == 1:
            mod_total = 'Modifier: {0}'.format(self.mod_total)
        else:
            mod_total = 'Modifiers: {0} | {1}'.format(self.mod_total, ', '.join(map(lambda x: str(x), self.modifiers)))

        if len(self.rolls) == 1 and len(self.modifiers) == 0:
            return str(self.rolls[0])
        elif len(self.modifiers) == 0:
            return total + roll_results
        else:
            return total + roll_results + mod_total


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
        text="Hi! This is a dice-rolling bot created by @foxscotch.\n" +
             "For help using this bot, type /help. For more info, type /about. Otherwise, use /roll to roll some dice.")

def about(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
        parse_mode='Markdown',
        text="As mentioned in the /start message, the bot's made by me, @foxscotch.\n" +
             "The bot's open source, as are most things I make, and you can see that source [on GitHub](https://github.com/foxscotch/foxrollbot).\n" +
             "If you have any questions, feel free to send me a message directly. I'll be happy to answer them if I can. " +
             "And if you find any bugs, either send me a message on Telegram, or open an issue on GitHub.")

def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
        parse_mode='Markdown',
        text="This bot just rolls dice. Aside from /start, /about, and /help, its only command is /roll. That command, however, is moderately complicated.\n\n" +

              "First of all, here's the syntax description, which you'll see if you send an invalid /roll:\n" +
              "`/roll <rolls>d<die>+[roll/modifier] [dis/adv] [x<qty>]`\n" +
              "Now, let's break that down, because it probably doesn't make a whole lot of sense right now.\n\n" +

              "First up we have `<rolls>d<die>`. Pretty simple, it's just a regular dice roll, like 1d20 or 2d8. Max rolls is 100, max die faces is 1000.\n" +
              "Then we have `+[roll/modifier]`. This whole thing is optional. It can be another roll like the first part, or just a plain number modifier " +
              "like 4 or 7, with a max of 1000. You can also use - instead of + to specify subtraction. You can have more than one of these sections, up to 25 total.\n" +
              "Lastly, there's `[dis/adv]`. It's probably the most confusing part. What it means is simply that you can add 'adv' or 'dis' to the roll. " +
              "'adv' or 'dis' can also just be 'a' or 'd', or in fact any amount of the words 'advantage' or 'disadvantage'. You can't use both in one roll.\n" +
              "The last bit, '[x<qty>]', should look something like 'x4' or 'x12'. It signifies that you want to roll that complete preceding roll that number of times.\n" +
              "Something the syntax description doesn't make clear is that you can have more than one _complete_ roll in one command, including those last additions.\n\n" +

              "For anyone who learns best by example, here's a few:\n" +
              "`/roll 1d20`\n" +
              "`/roll 1d20+2d8-4`\n" +
              "`/roll 1d6+2 adv x2`\n" +
              "`/roll 1d20 dis 2d4+6`")


def roll(bot, update, args):
    msg_args = {
        'chat_id': update.message.chat_id,
        'reply_to_message_id': update.message.message_id,
    }

    try:
        if len(args) == 0:
            raise InvalidSyntaxException()

        parts = []

        base_part = {
            'roll': None,
            'adv': False,
            'dis': False,
            'qty': 1
        }

        cur_part = base_part.copy()
        for arg in args:
            if arg[0].isdigit():
                if len(parts) > 1:
                    cur_part = base_part.copy()

                parts.append(cur_part)
                cur_part['roll'] = CompleteRoll.from_str(arg)
            else:
                if 'advantage'.startswith(arg):
                    cur_part['adv'] = True
                elif 'disadvantage'.startswith(arg):
                    cur_part['dis'] = True
                elif arg.startswith('x') and arg[1:].isdigit():
                    cur_part['qty'] = int(arg[1:])
                else:
                    raise InvalidSyntaxException()

        result_str = ''
        for part in parts:
            for i in range(part['qty']):
                if len(result_str) > 0:
                    result_str += '\n\n'

                r1, r2 = part['roll'].roll(), part['roll'].roll()

                if part['adv']:
                    if r1.total >= r2.total:
                        result_str += str(r1)
                        result_str += '\nOther roll: {0}'.format(r2.total)
                    else:
                        result_str += str(r2)
                        result_str += '\nOther roll: {0}'.format(r1.total)
                elif part['dis']:
                    if r1.total <= r2.total:
                        result_str += str(r1)
                        result_str += '\nOther roll: {0}'.format(r2.total)
                    else:
                        result_str += str(r2)
                        result_str += '\nOther roll: {0}'.format(r1.total)
                else:
                    result_str += str(r1)

        msg_args['text'] = result_str
    except InvalidSyntaxException as e:
        msg_args['text'] = 'Syntax: `/roll <rolls>d<die>+[roll/modifier] [dis/adv] [x<qty>]`'
    except FoxRollBotException as e:
        msg_args['text'] = str(e)

    bot.send_message(**msg_args)


def error_callback(bot, update, error):
    logging.error(error)


if __name__ == '__main__':
    updater = Updater(token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('about', about))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(RollCommandHandler('roll', roll, pass_args=True))

    dispatcher.add_error_handler(error_callback)

    #updater.start_webhook('127.0.0.1', 6969, token,
    #    webhook_url='https://bot.foxscotch.us/' + token)
    updater.start_polling()
