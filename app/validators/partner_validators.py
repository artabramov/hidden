from typing import Union


def validate_partner_name(partner_name: str = None) -> Union[str, None]:
    return partner_name.strip() if partner_name else None


def validate_partner_summary(partner_summary: str = None) -> Union[str, None]:
    if partner_summary is None:
        return None

    partner_summary = partner_summary.strip()
    return None if partner_summary == "" else partner_summary


def validate_partner_contacts(partner_contacts: str = None) -> Union[str, None]:
    if partner_contacts is None:
        return None

    partner_contacts = partner_contacts.strip()
    return None if partner_contacts == "" else partner_contacts
