"""API package: contains FastAPI application modules.

This package houses the primary API implementation while the top-level
`asset_management_server/*.py` files act as compatibility shims that re-export these
implementations to preserve existing import paths.
"""

__all__ = ["main", "auth", "crud"]
