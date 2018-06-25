import logging
import os

from telegram.ext import CommandHandler, MessageHandler
from telegram.ext.updater import Updater

from roll import RollCommand
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
        msg_args['text'] = RollCommand.from_args(args)
    except InvalidSyntaxException:
        msg_args['text'] = 'Syntax: ' + text['syntax']
        msg_args['parse_mode'] = 'Markdown'
    except FoxRollBotException as e:
        msg_args['text'] = str(e)

    bot.send_message(**msg_args)


def test(bot, update):
    import json
    msg = json.dumps(update.message.to_dict(), indent=True)
    bot.send_message(chat_id=update.message.chat_id, parse_mode='Markdown', text=f'```{msg}```')


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

    dispatcher.add_handler(MessageHandler(None, test))

    dispatcher.add_error_handler(error_callback)

    print('Starting bot...')
    updater.start_polling()
