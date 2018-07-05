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

    def save(self, user, chat, name, args):
        """
        Save a roll to the database.

        Args:
            user (int): User ID to save roll for
            chat (int): Chat ID to save roll for
            name (str): Name of saved roll
            args (list): Arguments to save for roll
        """
        pass

    def get(self, user, chat, name):
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

    def delete(self, user, chat, name):
        """
        Delete a saved roll from the database.

        Args:
            user (int): User ID to delete roll from
            chat (int): Chat ID to delete roll from
            name (str): Name of saved roll
        """
        pass
