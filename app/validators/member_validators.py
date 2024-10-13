from typing import Union


def validate_member_name(member_name: str = None) -> Union[str, None]:
    return member_name.strip() if member_name else None


def validate_member_summary(member_summary: str = None) -> Union[str, None]:
    if member_summary is None:
        return None

    member_summary = member_summary.strip()
    return None if member_summary == "" else member_summary


def validate_member_contacts(member_contacts: str = None) -> Union[str, None]:
    if member_contacts is None:
        return None

    member_contacts = member_contacts.strip()
    return None if member_contacts == "" else member_contacts
