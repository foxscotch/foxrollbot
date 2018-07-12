import os
import sqlite3
from pathlib import Path

from jinja2 import Template

from roll import RollCommand
from errors import *


class SavedRollManager:
    """
    Class for managing saved rolls.

    Attributes:
        db (str): URI of database used for connections
    """

    TABLE = 'saved_rolls'
    """str: Name of table in which to store saved rolls"""

    def __init__(self, db=None):
        """
        Create a SavedRollManager instance.

        If a connection is not passed, it will use a new in-memory database.

        Args:
            db (str): URI of database to connect to
        """
        if db is None:
            self.db = 'file:foxrollbot_db?mode=memory&cache=shared'
        else:
            self.db = db

        # This attribute is used to maintain a single connection to the
        # database, so that in-memory databases aren't just lost after every
        # connection is finished.
        self._main_connection = sqlite3.connect(self.db, uri=True)

        self._load_statements()
        self._init_db()

    def _init_db(self):
        """
        Ensure that the database is set up correctly, initializing it if
        necessary.
        """
        cursor = self._main_connection.cursor()
        cursor.execute(self.sql['create_table'])
        self._main_connection.commit()
    
    def _load_statements(self):
        """Load SQL statements from the ./sql directory."""
        home = Path('.')
        context = {'table_name': self.TABLE}
        self.sql = {}
        for path in home.glob('./sql/*'):
            with open(path) as f:
                template = Template(f.read().strip())
                self.sql[path.stem] = template.render(context)
    
    def connect(self):
        return sqlite3.connect(self.db, uri=True)

    def save(self, name, args, user):
        """
        Save a roll to the database.

        Args:
            name (str): Name of saved roll
            args (list): Arguments to save for roll
            user (int): User ID to save roll for
        """
        # Make sure the given arguments are valid first.
        RollCommand.from_args(args)

        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute(self.sql['save'], {'name': name,
                                          'args': ' '.join(args),
                                          'user': user})
        connection.commit()

    def get(self, name, user):
        """
        Get a saved roll from the database.

        Args:
            name (str): Name of saved roll
            user (int): User ID to get roll for

        Returns:
            list: List of arguments of saved roll
        """
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute(self.sql['get'], {'name': name,
                                         'user': user})
        result = cursor.fetchone()
        if result is not None:
            return result[0].split()
        else:
            raise DoesNotExistException(
                'Could not find an applicable saved roll with that name.')

    def delete(self, name, user):
        """
        Delete a saved roll from the database.

        Args:
            name (str): Name of saved roll
            user (int): User ID to delete roll from
        """
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute(self.sql['delete'], {'name': name,
                                            'user': user})
        if cursor.rowcount < 1:
            raise DoesNotExistException(
                'Could not find an applicable saved roll with that name.')
        connection.commit()
