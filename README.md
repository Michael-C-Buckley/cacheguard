# CacheGuard

A simple and secure Python datastore protected by [Sops](https://getsops.io/).

Comes in two varieties: simple key-value and simple text stores.

## Cache Types

* `KeyCache` - Simple key-value store
* `TextCache` - Simple text file store

## Requires

This is an integration with Sops, and will *require* a functional Sops setup.

For assistance with Sops, see their [documentation](https://getsops.io/docs/).

SUPPORT IDENTITIES CURRENTLY: Age, OpenPGP (AKA GPG)

Additional Sops identities are coming soon. 

## Sops Integrations

At-rest files can be examined if they are decrypted by sops, without needing an active Python session.  The type of file is "binary" from a sops perspective, this fully encrypts the body where keys are also not visible without decryption. Additionally, the binary type does not add newline characters to results, as the other Sops types do.

## Threat Models

This modules protects data at rest.  It does not protect data at run time.  It may be possible for other modules/processes/logging/etc to view it.

Potentially useful for operational caches and other sensitive record keeping that needs to be local and transferred via git.

## Examples

### Basic Logging with TextCache

```python
from cacheguard import TextCache
from datetime import datetime

# Initialize cache with Sops encryption keys
cache = TextCache(
    "logs.sops",
    age_pubkeys=["age1..."],  # List of Age keys, which can include SSH pubkeys as well now 
    pgp_fingerprints=["ABC123..."]  # Your PGP fingerprints
)

# Log some events
cache.append(f"[{datetime.now()}] Application started")
cache.append(f"[{datetime.now()}] User login: user123")
cache.append(f"[{datetime.now()}] Database connection established")

# Save encrypted logs
cache.save()
```

### Key-Value Storage with KeyCache

```python
from cacheguard import KeyCache

# Store sensitive configuration
config_vars = KeyCache("config.sops", age_pubkeys=["age1..."])
config_vars.add({"api_key": "secret123", "db_password": "secure456"})
config_vars.save()

# Load into environment variables
config_vars.deploy()  # Makes api_key and db_password available as env vars
```
