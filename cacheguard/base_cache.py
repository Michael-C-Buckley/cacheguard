# Python Modules
from datetime import datetime
from os import path
from pathlib import Path
from shutil import move

# Local Modules
from cacheguard.sops import encrypt, decrypt


class BaseCache:
    """Mechanism for sealing and protecting a dataset at rest"""

    def __init__(
        self,
        sops_path: str,
        age_pubkeys: list[str] = [],
        pgp_fingerprints: list[str] = [],
        *args,
        **kwargs,
    ) -> None:
        self.age_pubkeys = age_pubkeys
        self.pgp_fingerprints = pgp_fingerprints
        self.sops_path = sops_path

        self.data = self.load() if path.exists(sops_path) else ""

    def load(self) -> str:
        """Unseal the dataset"""
        try:
            with open(self.sops_path) as f:
                contents = f.read()
            data = decrypt(contents)
        except OSError:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_file_name = f"archive-{timestamp}-{Path(self.sops_path).name}"
            new_path = Path(self.sops_path).parent / new_file_name
            move(self.sops_path, new_path)
            print(
                f"[CacheGuard] Warning: Cache JSON error - old cache potentially corrupt or empty.\n - Created new one and archived original at: {new_path}"
            )
            return ""  # The file was not valid and was empty or corrupt
        else:
            return data

    def save(self, data_string) -> None:
        """Write the dataset to the encrypted at-rest state"""
        encrypted_data = encrypt(data_string)

        if not path.exists(self.sops_path):
            # make it
            Path(self.sops_path).parent.mkdir(parents=True, exist_ok=True)
            Path(self.sops_path).touch(exist_ok=True)
        with open(self.sops_path, "w") as f:
            f.write(encrypted_data)

    def add(self):
        """"""
        raise NotImplementedError("Incorrect cache type - method for Key Cache")

    def append(self):
        """"""
        raise NotImplementedError("Incorrect cache type - method for Text Cache")
