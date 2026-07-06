class NoActiveDatasetException(Exception):
    """
    Raised when an operational backend service requests dataset-scoped data,
    but no active dataset is currently registered in the database.
    """
    def __init__(self, message: str = "No active dataset selected. Please activate a dataset to begin analysis."):
        self.message = message
        super().__init__(self.message)
