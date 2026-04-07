"""Barcode parsing utilities for SmartBU EOL automation.

Expected 2D barcode format (19 characters):
    pppp r v 1 qq yy ddd sssss

Where:
- pppp: last 4 digits of SAP part number
- r: drawing revision (1-9 or A-Z)
- v: vendor code (1-9)
- 1: supplier assembly line (fixed literal '1')
- qq: optimisation index (2 digits)
- yy: production year (2 digits)
- ddd: day of year (001-366)
- sssss: unique serial number (5 digits)
"""

from __future__ import annotations

import re
from typing import Dict, Tuple

_BARCODE_RE = re.compile(
    r"^(?P<sap_last4>\d{4})"
    r"(?P<revision>[1-9A-Z])"
    r"(?P<vendor>[1-9])"
    r"(?P<assy_line>1)"
    r"(?P<opt_index>\d{2})"
    r"(?P<year>\d{2})"
    r"(?P<day_of_year>\d{3})"
    r"(?P<unique_serial>\d{5})$"
)


def normalize_barcode(raw: str) -> str:
    """Normalize scanner input by trimming spaces and upper-casing."""
    return "".join((raw or "").strip().split()).upper()


def parse_barcode(raw: str) -> Tuple[bool, str, Dict[str, str]]:
    """Validate and parse barcode input.

    Returns:
        tuple: (is_valid, error_message, parsed_fields)
    """
    barcode = normalize_barcode(raw)
    if not barcode:
        return False, "Barcode is empty.", {}

    if len(barcode) != 19:
        return False, "Barcode must be exactly 19 characters.", {}

    match = _BARCODE_RE.match(barcode)
    if not match:
        return (
            False,
            "Barcode format invalid. Expected pppprv1qqyydddsssss.",
            {},
        )

    fields = match.groupdict()
    day_of_year = int(fields["day_of_year"])
    if day_of_year < 1 or day_of_year > 366:
        return False, "Day-of-year (ddd) must be 001..366.", {}

    fields["barcode_19"] = barcode
    # Derived production serial requested in GUI flow: 16 digits without r/v/line.
    fields["pcb_serial_16"] = (
        f"{fields['sap_last4']}"
        f"{fields['opt_index']}"
        f"{fields['year']}"
        f"{fields['day_of_year']}"
        f"{fields['unique_serial']}"
    )
    fields["production_date_code"] = f"20{fields['year']}-DOY-{fields['day_of_year']}"

    return True, "", fields
