"""19-Character Barcode Parser — SmartBU EOL
============================================
Validates and parses the 2D barcode scanned for each DUT (Device Under Test).

Barcode standard: exactly 19 printable characters (no whitespace).

Field layout (0-based slice positions):
  Chars  1– 2  (slice  0: 2)  Supplier code     — 2 chars
  Chars  3–10  (slice  2:10)  Part number       — 8 chars
  Chars 11–14  (slice 10:14)  Production YYWW   — 4 chars  (e.g. 2501 = 2025 wk 01)
  Chars 15–19  (slice 14:19)  PCB serial        — 5 chars

  Example barcode: "US12345678250100001"
    supplier_code : "US"
    part_number   : "12345678"
    year_week     : "2501"
    pcb_serial    : "00001"

Adjust the slice constants below if the actual barcode format differs.
"""

from __future__ import annotations

# ── Barcode specification ──────────────────────────────────────────────────────
BARCODE_LENGTH = 19   # must be exactly this many non-whitespace characters

# ── Field slice positions (0-based, end exclusive) ────────────────────────────
# Change these if the barcode format is different in production.
_SUPPLIER_SLICE  = slice(0, 2)    # chars 1-2   : Supplier / plant code
_PART_NO_SLICE   = slice(2, 10)   # chars 3-10  : Part number
_YEAR_WEEK_SLICE = slice(10, 14)  # chars 11-14 : Production year+week (YYWW)
_SERIAL_SLICE    = slice(14, 19)  # chars 15-19 : PCB serial sequence


def is_valid(barcode: str) -> bool:
    """Return ``True`` when *barcode* is exactly 19 non-whitespace characters."""
    return len(barcode.strip()) == BARCODE_LENGTH


def parse(barcode: str) -> dict:
    """Parse a 19-character barcode string into named fields.

    Returns a dictionary with the following keys::

        {
            "raw":           "<full 19-char barcode>",
            "supplier_code": "<2 chars>",
            "part_number":   "<8 chars>",
            "year_week":     "<4 chars>",
            "pcb_serial":    "<5 chars>",
        }

    Returns an **empty dict** when *barcode* is not exactly 19 characters so
    callers can treat an empty result as an invalid barcode without raising.
    """
    barcode = barcode.strip()
    if len(barcode) != BARCODE_LENGTH:
        return {}
    return {
        "raw":           barcode,
        "supplier_code": barcode[_SUPPLIER_SLICE],
        "part_number":   barcode[_PART_NO_SLICE],
        "year_week":     barcode[_YEAR_WEEK_SLICE],
        "pcb_serial":    barcode[_SERIAL_SLICE],
    }
