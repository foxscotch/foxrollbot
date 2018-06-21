import logging

from telegram.ext import CommandHandler, MessageHandler
from telegram.ext.updater import Updater

from roll import DiceRoll, RollResult, CompleteRoll, CompleteRollResult
from errors import InvalidSyntaxException,  \
                   NotANumberException,     \
                   OutOfRangeException,     \
                   TooManyPartsException


logging.basicConfig(level=logging.INFO, filename='log.txt',
                    format='%(asctime)s %(name)s %(levelname)s: %(message)s')


with open('token.txt') as token_file:
    token = token_file.read().strip()


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
        text="Hi! This is a dice-rolling bot created by @foxscotch. "
             "For help using this bot, type /help. For more info, type /about. Otherwise, use /roll to roll some dice.")

def about(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
        parse_mode='Markdown',
        text="As mentioned in the /start message, the bot's made by @foxscotch.\n"
             "The bot's open source, as are most things I make, and you can see that source [on GitHub](https://github.com/foxscotch/foxrollbot). "
             "If you have any questions, feel free to send me a message directly. I'll be happy to answer them if I can. "
             "And if you find any bugs, either send me a message on Telegram, or open an issue on GitHub.")

def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
        parse_mode='Markdown',
        text="This bot just rolls dice. Aside from /start, /about, and /help, its only command is /roll. That command, however, is moderately complicated.\n\n"

              "First of all, here's the syntax description, which you'll see if you send an invalid /roll:\n"
              "`/roll <rolls>d<die>+[roll/modifier] [dis/adv] [x<qty>]`\n"
              "Now, let's break that down, because it probably doesn't make a whole lot of sense right now.\n\n"

              "First up we have `<rolls>d<die>`. Pretty simple, it's just a regular dice roll, like 1d20 or 2d8. Max rolls is 100, max die faces is 1000.\n"
              "Then we have `+[roll/modifier]`. This whole thing is optional. It can be another roll like the first part, or just a plain number modifier "
              "like 4 or 7, with a max of 1000. You can also use - instead of + to specify subtraction. You can have more than one of these sections, up to 25 total.\n"
              "Lastly, there's `[dis/adv]`. It's probably the most confusing part. What it means is simply that you can add 'adv' or 'dis' to the roll. "
              "'adv' or 'dis' can also just be 'a' or 'd', or in fact any amount of the words 'advantage' or 'disadvantage'. You can't use both in one roll.\n"
              "The last bit, '[x<qty>]', should look something like 'x4' or 'x12'. It signifies that you want to roll that complete preceding roll that number of times.\n"
              "Something the syntax description doesn't make clear is that you can have more than one _complete_ roll in one command, including those last additions.\n\n"

              "For anyone who learns best by example, here's a few:\n"
              "`/roll 1d20`\n"
              "`/roll 1d20+2d8-4`\n"
              "`/roll 1d6+2 adv x2`\n"
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
                cur_part = base_part.copy()
                parts.append(cur_part)
                cur_part['roll'] = CompleteRoll.from_str(arg)
            else:
                if cur_part['roll'] is None:
                    raise InvalidSyntaxException()

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
        msg_args['parse_mode'] = 'Markdown'
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
    dispatcher.add_handler(CommandHandler('roll', roll, pass_args=True))

    dispatcher.add_error_handler(error_callback)

    print('Starting bot...')
    updater.start_polling()
