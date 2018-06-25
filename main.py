import logging
import os

from telegram.ext import CommandHandler
from telegram.ext.updater import Updater

from roll import CompleteRoll
from errors import FoxRollBotException,     \
                   InvalidSyntaxException


logging.basicConfig(level=logging.INFO,  # filename='log.txt',
                    format='%(asctime)s %(name)s %(levelname)s: %(message)s')


text = {}
for file_name in os.listdir('./text'):
    with open('./text/' + file_name) as f:
        text[file_name] = f.read().strip()


def start_cmd(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text=text['start'])


def about_cmd(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode='Markdown',
                     text=text['about'])


def help_cmd(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode='Markdown',
                     text=text['help'])


def roll_cmd(bot, update, args):
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
    except InvalidSyntaxException:
        msg_args['text'] = 'Syntax: ' + text['syntax']
        msg_args['parse_mode'] = 'Markdown'
    except FoxRollBotException as e:
        msg_args['text'] = str(e)

    bot.send_message(**msg_args)


def error_callback(bot, update, error):
    logging.error(error)


if __name__ == '__main__':
    with open('token.txt') as token_file:
        token = token_file.read().strip()
    
    updater = Updater(token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start_cmd))
    dispatcher.add_handler(CommandHandler('about', about_cmd))
    dispatcher.add_handler(CommandHandler('help', help_cmd))
    dispatcher.add_handler(CommandHandler('roll', roll_cmd, pass_args=True))

    dispatcher.add_error_handler(error_callback)

    print('Starting bot...')
    updater.start_polling()
