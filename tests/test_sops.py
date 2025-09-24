"""
Test for the `cacheguard.sops` module, which contains helper functions for
interfacing with Sops via Subprocess
"""

from cacheguard.sops import encrypt

# These are dummy values
TEST_AGE_PUBKEY = (
    "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINylqNJ7MbeAA/YYa0rXQhFukbnXh0ZFKNQISigutI2v"
)
TEST_GPG_FINGERPRINT = "31F5A7299414BD57611F2A2A28737947AD89864B"
TEST_DATA = "This is only a test"


def test_encryption(mocker, monkeypatch):
    mock_run = mocker.patch("cacheguard.sops.run")

    def shutil_patch(*args, **kwargs):
        return "sops"

    monkeypatch.setattr("cacheguard.sops.which", shutil_patch)

    test_kwargs = {
        "data": TEST_DATA,
        "age_pubkeys": [TEST_AGE_PUBKEY],
        "pgp_fingerprints": [TEST_GPG_FINGERPRINT],
    }

    expected_call_args = [
        "sops",
        "-e",
        "-a",
        TEST_AGE_PUBKEY,
        "-p",
        TEST_GPG_FINGERPRINT,
        "/dev/stdin",
    ]

    expected_call = {
        "input": TEST_DATA,
        "capture_output": True,
        "text": True,
        "timeout": 4,
    }

    encrypt(**test_kwargs)

    mock_run.assert_called_with(expected_call_args, **expected_call)
