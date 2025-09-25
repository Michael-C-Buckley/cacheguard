# Python Modules
from io import StringIO

# Project Modules
from cacheguard.base_cache import BaseCache


class TextCache(BaseCache):
    """Plain-text edition of the cache"""

    def __init__(
        self,
        sops_path: str,
        age_pubkeys: list[str] = [],
        pgp_fingerprints: list[str] = [],
        newline: str = "\n",
    ):
        raw_data = super().__init__(sops_path, age_pubkeys, pgp_fingerprints)
        self.buffer = StringIO()
        self.newline = newline

        # Add the existing data
        for line in raw_data.split(newline):
            self.append(line)

    def load(self) -> str:
        """Handle the plain text version of the cache"""
        data = super().load()
        self.buffer = StringIO(data)
        return data

    def save(self) -> None:
        """Write the dataset to the encrypted at-rest state"""
        super().save(self.buffer.getvalue().strip())

    def append(self, string: str) -> None:
        """Simple method to add more string content"""
        self.buffer.write(string + self.newline)
