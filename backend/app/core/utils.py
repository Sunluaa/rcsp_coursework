import re
import secrets
import unicodedata


def slugify(value: str, fallback_prefix: str = "item") -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    if not slug:
        slug = f"{fallback_prefix}-{secrets.token_hex(4)}"
    return slug[:140]
