import sqlite3


connection = sqlite3.connect('data.db')


class SavedRoll:
    @staticmethod
    def save(user, name, args):
        pass

    @staticmethod
    def get(user, name):
        pass

    @staticmethod
    def delete(user, name):
        pass
