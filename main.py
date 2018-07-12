import logging
import os

from telegram.ext import CommandHandler, MessageHandler
from telegram.ext.updater import Updater

from db import SavedRollManager
from roll import RollCommand
from errors import *


logging.basicConfig(level=logging.INFO,  # filename='log.txt',
                    format='%(asctime)s %(name)s %(levelname)s: %(message)s')


text = {}
for file_name in os.listdir('./text'):
    with open('./text/' + file_name) as f:
        text[file_name] = f.read().strip()

# Just going to use the default in-memory database for now.
srm = SavedRollManager()


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
        'parse_mode': 'Markdown'
    }

    try:
        if len(args) < 1:
            raise NotEnoughArgumentsException(
                'Rolling dice requires at least one argument.')

        if args[0][0].isalpha():
            args = srm.get(args[0], update.message.from_user.id)
        msg_args['text'] = str(RollCommand.from_args(args))
    except InvalidSyntaxException:
        msg_args['text'] = f"Syntax: {text['roll_syntax']}"
    except FoxRollBotException as e:
        msg_args['text'] = str(e)

    bot.send_message(**msg_args)


def save_cmd(bot, update, args):
    msg_args = {
        'chat_id': update.message.chat_id,
        'reply_to_message_id': update.message.message_id,
        'parse_mode': 'Markdown'
    }

    try:
        srm.save(args[0], args[1:], update.message.from_user.id)
        msg_args['text'] = f"Roll successfully saved as `{args[0]}`!"
    except InvalidSyntaxException:
        msg_args['text'] = f"Syntax: {text['save_syntax']}"
    except FoxRollBotException as e:
        msg_args['text'] = str(e)

    bot.send_message(**msg_args)


def delete_cmd(bot, update, args):
    msg_args = {
        'chat_id': update.message.chat_id,
        'reply_to_message_id': update.message.message_id,
        'parse_mode': 'Markdown'
    }

    try:
        srm.delete(args[0], update.message.from_user.id)
        msg_args['text'] = f"Successfully deleted `{args[0]}`."
    except FoxRollBotException as e:
        msg_args['text'] = str(e)

    bot.send_message(**msg_args)


def test(bot, update):
    # Only reply if @foxscotch sent the message
    if update.message.from_user.id == 136418592:
        import json
        msg = json.dumps(update.message.to_dict(), indent=True)
        bot.send_message(chat_id=update.message.chat_id,
                         parse_mode='Markdown',
                         text=f'```{msg}```')


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
    dispatcher.add_handler(CommandHandler('save', save_cmd, pass_args=True))
    dispatcher.add_handler(CommandHandler('delete', delete_cmd, pass_args=True))

    dispatcher.add_handler(MessageHandler(None, test))

    dispatcher.add_error_handler(error_callback)

    print('Starting bot...')
    updater.start_polling()
