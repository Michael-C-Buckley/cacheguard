# Python Modules
from io import StringIO

# Project Modules
from cacheguard.base_cache import BaseCache

# Third-Party Modules
from sopsy import SopsyInOutType


class TextCache(BaseCache):
    """Plain-text edition of the cache"""

    def __init__(self, sops_file: str, file_type: SopsyInOutType):
        self.buffer = StringIO()
        super().__init__(sops_file, file_type)

    def load(self) -> str:
        """Handle the plain text version of the cache"""
        data = super().load()
        self.buffer = StringIO(data)
        return data

    def save(self) -> None:
        """Write the dataset to the encrypted at-rest state"""
        with open(self.sops_file, "w") as file:
            file.write(self.buffer.getvalue())
        super().save()

    def append(self, string: str) -> None:
        """Simple method to add more string content"""
        self.buffer.write(string)
