# exception.py

class TransferError(Exception):
    """Exception thrown when an error occurs while downloading/uploading file."""

    def __init__(self, value):
        self.value = value

    def _str_(self):
        return repr(self.value)
