import re
from typing import Annotated

from email_validator import EmailNotValidError, validate_email
from pydantic import AfterValidator


LOCAL_PART_PATTERN = re.compile(r"^[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*$")
DOMAIN_LABEL_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")


def normalize_email(value: str) -> str:
    email = value.strip()
    try:
        return validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError as exc:
        local_email = normalize_local_email(email)
        if local_email is not None:
            return local_email
        raise ValueError(str(exc)) from exc


def normalize_local_email(email: str) -> str | None:
    if email.count("@") != 1:
        return None

    local_part, domain = email.rsplit("@", 1)
    domain = domain.lower()

    if not local_part or not domain.endswith(".local"):
        return None
    if not LOCAL_PART_PATTERN.fullmatch(local_part):
        return None

    labels = domain.split(".")
    if any(not DOMAIN_LABEL_PATTERN.fullmatch(label) for label in labels):
        return None

    return f"{local_part}@{domain}"


EmailAddress = Annotated[str, AfterValidator(normalize_email)]
