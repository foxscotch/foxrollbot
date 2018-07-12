import os


class Text:
    """
    Class for managing texts retrieved from a directory of text files.

    After instantiation, texts can be retrieved through attribute access, for
    instance, the following example will create a Text instance and print the
    contents of the ./text/about file:

        >>> t = Text('./text')
        >>> print(t.about)
    """
    def __init__(self, directory):
        """
        Create a new Text object.
        
        Args:
            directory (str): Directory in which to find text files
        """
        self._texts = {}
        for file_name in os.listdir(directory):
            with open(os.path.join(directory, file_name)) as f:
                self._texts[file_name] = f.read().strip()
    
    def __getattr__(self, attr):
        if attr in self._texts:
            return self._texts[attr]
        else:
            raise AttributeError()
