from roll import Roll


class SavedRollManager:
    """
    Class for managing saved rolls.

    Attributes:
        connection (sqlite3.Connection): Database connection used by manager
    """

    def __init__(self, connection):
        """
        Create a SavedRollManager instance.

        Args:
            connection (sqlite3.Connection): Database connection to use
        """
        self.connection = connection
        self._init_db()

    def _init_db(self):
        """
        Ensures that the database is set up correctly, initializing it if
        necessary.
        """
        self.connection.cursor().execute(
            'CREATE TABLE IF NOT EXISTS saved_rolls ('
            'id INTEGER PRIMARY KEY AUTOINCREMENT,'
            'name VARCHAR(32),'
            'arguments TEXT NOT NULL,'
            'user_id INTEGER,'
            'chat_id INTEGER);')
        self.connection.commit()

    def save(self, name, args, user=None, chat=None):
        """
        Save a roll to the database.

        Args:
            user (int): User ID to save roll for
            chat (int): Chat ID to save roll for
            name (str): Name of saved roll
            args (list): Arguments to save for roll
        """
        # Try to create a Roll from the arguments, to make sure they're valid.
        # It'll raise an error if it's bad, and it turns out that's what we
        # want, so we can just save right afterwards, no try necessary.
        Roll.from_args(args)

        # Other than that check, I think this might already be enough, actually.
        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO saved_rolls VALUES (?, ?, ?, ?, ?)',
                       (None, name, ' '.join(args), user, chat))

    def get(self, name, user=None, chat=None):
        """
        Get a saved roll from the database.

        Args:
            user (int): User ID to get roll for
            chat (int): Chat ID to get roll for
            name (str): Name of saved roll

        Returns:
            list: List of arguments of saved roll
        """
        pass

    def delete(self, name, user=None, chat=None):
        """
        Delete a saved roll from the database.

        Args:
            user (int): User ID to delete roll from
            chat (int): Chat ID to delete roll from
            name (str): Name of saved roll
        """
        pass
