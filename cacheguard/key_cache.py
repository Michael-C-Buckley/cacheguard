# Python Modules
from os import environ

# Project Modules
from cacheguard.base_cache import BaseCache

# Third-Party Modules
from orjson import dumps, loads


class KeyCache(BaseCache):
    """Key-Value edition of the Cache"""

    def __init__(self, sops_file: str):
        self.data = {}
        super().__init__(sops_file)

    def load(self) -> str:
        """Handle the data for key-values by loading with JSON"""
        self.data = loads(super().load())
        return self.data

    def save(self):
        """Write the dataset to the encrypted at-rest state"""
        with open(self.sops_file, "w") as file:
            file.write(dumps(self.data).decode())
        super().save()

    def add(self, entry: dict):
        """Add a new entry"""
        self.data = {**self.data, **entry}

    def load_env_var(self, env_var):
        """Load a key-value pair into the environment from the cache"""
        if not self.data.get(env_var):
            raise KeyError("Key does not exist in Key Cache")
        environ[env_var] = self.data[env_var]

    def deploy(self):
        """Load every key-value pair in this cache into the environment"""
        for key in self.data.keys():
            self.load_env_var(key)
