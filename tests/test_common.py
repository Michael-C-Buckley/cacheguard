# Tooling used for creating parameterized tests


def generate_params(key_str: str):
    """Generate params and use either encrypt or decrypt"""
    return [
        ("age", f"cacheguard.base_cache.age_{key_str}crypt"),
        ("sops", f"cacheguard.base_cache.sops_{key_str}crypt"),
    ]


def decrypt_params():
    return generate_params("de")


def encrypt_params():
    return generate_params("en")
