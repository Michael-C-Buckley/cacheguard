# Nix Development

Here is a basic provided nix shell for development.  I use it as a NixOS developer, however, I use the minimum plumbing to get a "typical" python development experience using virtual environments and not nix for python dependencies.  

## Suggested `.envrc`

Here is a simple Direnv hook to use the development environment here.

```
use flake
layout python3
export UV_PROJECT_ENVIRONMENT="$VIRTUAL_ENV"
export UV_SYSTEM_PYTHON="1"
```