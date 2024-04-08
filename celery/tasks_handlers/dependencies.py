import boto3
from singleton_decorator import singleton


@singleton
class DependencyManager:
    """
    Define class with all dependencies.
    """

    def __init__(self):
        self._s3_client = None

    @property
    def s3_client(self):
        if self._s3_client is None:
            self._s3_client = boto3.client('s3')
        return self._s3_client
