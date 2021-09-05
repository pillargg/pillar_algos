"""
Custom defined exceptions that can be raised by algorithms
"""


# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""

    pass


class MissingColumnError(Error):
    """
    Raised when the a column is missing from the dataframe
    """

    def __init__(self, col: str, message: str = "Not found in dataframe.columns"):
        self.col = col
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """
        Custom message output
        """
        return f"{self.col} -> {self.message}"


class DuplicatesFoundError(Error):
    """
    Raised when dataframe contains duplicate rows
    """

    def __init__(self, message: str = "Duplicates found in the dataframe"):
        self.message = message
        super().__init__(self.message)


class ExpectedOneValueError(Error):
    """
    Raised when a my_series.unique() is supposed to only have 1
    unique value, but multiple was found
    """

    def __init__(
        self, num_unique: int, message: str = "Expect 1 unique value but found"
    ):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} {self.num_unique}"


class VidIdNotFound(Error):
    '''
    Raised by cccLabeler() if the provided vid_id is not amongst the vid_ids in the ccc dataset
    '''
    
    def __init__(self, vid_id: int):
        self.message = f"{vid_id} vid_id was not found in the CCC dataset"
        super().__init__(self.message)