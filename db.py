import os
from pathlib import Path

from jinja2 import Template

from roll import RollCommand
from errors import *


class SavedRollManager:
    """
    Class for managing saved rolls.

    Attributes:
        connection (sqlite3.Connection): Database connection used by manager
    """

    TABLE = 'saved_rolls'
    """str: Name of table in which to store saved rolls"""

    def __init__(self, connection):
        """
        Create a SavedRollManager instance.

        Args:
            connection (sqlite3.Connection): Database connection to use
        """
        self.connection = connection
        self._load_statements()
        self._init_db()

    def _init_db(self):
        """
        Ensure that the database is set up correctly, initializing it if
        necessary.
        """
        cursor = self.connection.cursor()
        cursor.execute(self.sql['create_table'])
        self.connection.commit()
    
    def _load_statements(self):
        """Load SQL statements from the ./sql directory."""
        home = Path('.')
        context = {'table_name': self.TABLE}
        self.sql = {}
        for path in home.glob('./sql/*'):
            with open(path) as f:
                template = Template(f.read().strip())
                self.sql[path.stem] = template.render(context)

    def save(self, name, args, user=None, chat=None):
        """
        Save a roll to the database.

        Args:
            name (str): Name of saved roll
            args (list): Arguments to save for roll
            user (int): User ID to save roll for
            chat (int): Chat ID to save roll for
        """
        # Make sure the given arguments are valid first.
        RollCommand.from_args(args)
        
        cursor = self.connection.cursor()
        cursor.execute(self.sql['save'], {'name': name,
                                          'args': ' '.join(args),
                                          'user': user,
                                          'chat': chat})
        self.connection.commit()

    def get(self, name, user=None, chat=None):
        """
        Get a saved roll from the database.

        Args:
            name (str): Name of saved roll
            user (int): User ID to get roll for
            chat (int): Chat ID to get roll for

        Returns:
            list: List of arguments of saved roll
        """
        cursor = self.connection.cursor()
        cursor.execute(self.sql['get'], {'name': name,
                                         'user': user,
                                         'chat': chat})
        result = cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            raise DoesNotExistException(
                'Could not find an applicable saved roll with that name.')

    def delete(self, name, user=None, chat=None):
        """
        Delete a saved roll from the database.

        Args:
            name (str): Name of saved roll
            user (int): User ID to delete roll from
            chat (int): Chat ID to delete roll from
        """
        cursor = self.connection.cursor()
        cursor.execute(self.sql['delete'], {'name': name,
                                            'user': user,
                                            'chat': chat})
        self.connection.commit()
