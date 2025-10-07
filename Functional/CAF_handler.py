import os
import pandas as pd
import binascii



# ----------------------------
# Module-level state
# ----------------------------
parameters_df = None
hex_bytes = []
modified_byte_indices = set()

# ----------------------------
# CRC / hex‑byte utilities
# ----------------------------
def calculate_crc16_ccitt_false(data_bytes: bytes) -> int:
    return binascii.crc_hqx(data_bytes, 0xFFFF)

def convert_hex_string_to_bytes(hex_string: str) -> bytes:
    hex_parts = [byte for byte in hex_string.strip().split() if byte]
    if not hex_parts:
        raise ValueError("Empty hex string.")
    ba = []
    for b in hex_parts:
        if len(b) != 2:
            raise ValueError(f"Invalid byte '{b}', must be 2 hex digits.")
        try:
            ba.append(int(b, 16))
        except ValueError:
            raise ValueError(f"Invalid hex byte '{b}'.")
    return bytes(ba)

# ----------------------------
# Excel loading & parameter lookup
# ----------------------------
def load_and_validate_excel(excel_file_path: str):
    global parameters_df
    if not os.path.exists(excel_file_path):
        raise FileNotFoundError(f"Excel file not found: {excel_file_path}")
    sheets = pd.read_excel(excel_file_path, sheet_name=None)
    merged = pd.concat([sheet.rename(columns=str.strip) for sheet in sheets.values()],
                       ignore_index=True)
    required_cols = [
        "Parameter Name (code beamer)",
        "Physical Default Value y",
        "Validity physical upper threshold",
        "Validity physical lower threshold",
        "Position index in tp coding stream"
    ]
    for col in required_cols:
        if col not in merged.columns:
            raise ValueError(f"Missing column in Excel: {col}")
    merged["_param_normalized"] = merged["Parameter Name (code beamer)"] \
        .astype(str).str.strip().str.lower()
    parameters_df = merged

def find_parameter_row(parameter_name: str):
    global parameters_df
    if parameters_df is None:
        return None
    norm = parameter_name.strip().lower()
    row = parameters_df[parameters_df["_param_normalized"] == norm]
    if row.empty:
        return None
    return row.iloc[0]

# ----------------------------
# Hex operations
# ----------------------------
def load_hex_string(hex_string: str):
    global hex_bytes, modified_byte_indices
    parts = [b for b in hex_string.replace("\n", " ").split() if b]
    # validate tokens
    for b in parts:
        if len(b) != 2 or any(c not in "0123456789abcdefABCDEF" for c in b):
            raise ValueError(f"Invalid hex token '{b}'")
    hex_bytes = [b.upper() for b in parts]
    modified_byte_indices = set()

def display_hex_with_highlights() -> str:
    return " ".join(
        f"[{hex_bytes[i]}]" if i in modified_byte_indices else hex_bytes[i]
        for i in range(len(hex_bytes))
    )

def get_raw_hex_string() -> str:
    return " ".join(hex_bytes)

def modify_hex_byte(byte_index: int, new_byte_value: str):
    global hex_bytes, modified_byte_indices
    if not (0 <= byte_index < len(hex_bytes)):
        raise IndexError("Byte index out of range")
    nb = new_byte_value.strip().upper()
    if len(nb) != 2 or any(c not in "0123456789ABCDEF" for c in nb):
        raise ValueError("New value must be a 2‑digit hex")
    hex_bytes[byte_index] = nb
    modified_byte_indices.add(byte_index)

def crc16_ccitt_false_from_hexstream(hexstream: str) -> int:
    """
    Compute CRC16 CCITT‑FALSE of a comma separated hex byte stream.
    E.g. "3D,01,08,06,3A,00,98,81" → integer CRC value (0–0xFFFF).
    """
    # parse the hex bytes
    parts = hexstream.split()
    data = bytearray(int(p, 16) for p in parts if p.strip() != '')
    
    # compute CRC‑16/CCITT‑FALSE
    crc = 0xFFFF
    poly = 0x1021
    
    for b in data:
        crc ^= (b << 8)
        for _ in range(8):
            if (crc & 0x8000) != 0:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFFFF  # keep to 16 bits
    
    return crc

def calculate_crc_for_current_hex() -> str:
    raw = get_raw_hex_string()
    crc = crc16_ccitt_false_from_hexstream(raw)
    low_byte = crc & 0xFF
    high_byte = (crc >> 8) & 0xFF
    return f"{low_byte:02X} {high_byte:02X}"

def get_hex_string_with_crc() -> str:
    return get_raw_hex_string() + " " + calculate_crc_for_current_hex()

# ----------------------------
# Non‑interactive apply modifications
# ----------------------------
def apply_modifications(hex_input: str,
                        excel_path: str,
                        modifications: dict[str, str]) -> str:
    """
    hex_input: string of hex bytes (e.g. "AA BB 01 ...")
    excel_path: path to the Excel file with parameter definitions
    modifications: mapping of parameter name → new hex value (2-digit string)
    
    Returns the final HEX string including CRC appended.
    """
    # load Excel parameters
    load_and_validate_excel(excel_path)
    # load initial hex
    load_hex_string(hex_input)
    
    # apply modifications
    for param_name, new_hex in modifications.items():
        row = find_parameter_row(param_name)
        if row is None:
            # optional: raise or skip
            raise KeyError(f"Parameter '{param_name}' not found in Excel")
        # position index may be float or string, convert to integer
        pos = int(float(row["Position index in tp coding stream"]))
        modify_hex_byte(pos, new_hex)
    
    # produce output
    # (you can also return display format, or both)
    final_hex = get_hex_string_with_crc()
    return final_hex

# ----------------------------
# Example usage (for testing or embedding)
# ----------------------------

excel_file = r"D:\CAF Datas\XNF\XNF_TP_coding_file_v2.3_P3.2.0.xlsx"
# Suppose your input hex string is:
input_hex = "03 02 00 00 00 00 E8 03 3C DC 05 50 58 1B 64 00 00 00 DC 05 3C A0 0F 50 58 1B 64 00 00 00 E8 03 3C DC 05 50 58 1B 64 00 00 00 DC 05 3C A0 0F 50 58 1B 64 B0 04 00 00 64 00 C8 00 F8 07 B8 0B 88 13 A4 06 00 00 96 00 79 01 4E 07 A0 0F 58 1B 30 75 00 00 A0 0F 10 27 30 75 50 C3 60 EA 00 1E 3C 3C 1E 00 B0 04 00 00 64 00 C8 00 F8 07 B8 0B 88 13 A4 06 00 00 96 00 79 01 4E 07 A0 0F 58 1B 30 75 00 00 A0 0F 10 27 30 75 50 C3 60 EA 00 1E 3C 3C 1E 00 B0 04 00 00 64 00 C8 00 F8 07 B8 0B 88 13 A4 06 00 00 96 00 79 01 4E 07 A0 0F 58 1B 30 75 00 00 A0 0F 10 27 30 75 50 C3 60 EA 00 1E 3C 3C 1E 00 B0 04 00 00 64 00 C8 00 F8 07 B8 0B 88 13 A4 06 00 00 96 00 79 01 4E 07 A0 0F 58 1B 30 75 00 00 A0 0F 10 27 30 75 50 C3 60 EA 00 1E 3C 3C 1E 00 00 21 24 1D 49 18 6D 15 92 13 B6 10 DB 0E FF 0C 00 2D 24 24 49 1C 6D 16 92 13 B6 10 DB 0B FF 08 00 17 24 15 49 15 6D 15 92 14 B6 12 DB 0F FF 0D 00 16 24 15 49 15 6D 15 92 14 B6 12 DB 0F FF 0D 20 03 E8 03 3C 3C FF FF FF FF FF FF FF FF 32 00 28 00 D4 30 C8 F4 01 F4 01 19 01 00 1E 01 00 32 01 00 5A 01 00 6E 01 00 9B 01 00 BE 01 00 19 01 00 1E 01 00 32 01 00 5A 01 00 6E 01 00 9B 01 00 BE 01 00 5C 44 14 98 3A 3C FF FF FF FF FF FF FF FF FF FF FF FF FF FF 10 27 1E CA 08 DC 05 64 88 13 10 27 32 CA 08 DC 05 8C 70 17 10 27 32 CA 08 DC 05 8C 58 1B 10 27 28 70 17 08 07 78 88 13 10 27 32 38 18 DC 05 78 88 13 10 27 32 00 19 AC 0D 78 40 1F 19 19 7D 3C 32 0A 19 32 14 1D 1D 23 04 5A 32 FF FF FF FF FF 5A 50 50 04 64 28 18 0A FF FF FF FF FF FF FF FF FF 06 05 02 02 4B 04 FF FF FF FF FF FF FF FF 41 2C 01 37 FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF C8 00 9C FF 03 01 01 FF FF FF FF FF FF FF FF 90 01 38 FF 01 03 01 FF FF FF FF FF FF FF FF 0E 01 79 FF 01 01 03 FF FF FF FF FF FF FF FF 3C 00 E2 FF 03 01 01 FF FF FF FF FF FF FF FF C8 00 9C FF 01 03 01 FF FF FF FF FF FF FF FF 50 00 D8 FF 01 01 03 FF FF FF FF FF FF FF FF"
# And you want to modify parameter "ParamFoo" to new hex "5A",
# and "ParamBar" to new hex "B3"
modifications = {
    "PAR_LOCK_SENSOR_DEBOUNCE_TIME": "5B",
    "PAR_UNLOCK_SENSOR_DEBOUNCE_TIME": "04",
    "PAR_ADS_DOOR_CLOSED_DEBOUNCE_TIME_XNF": "19",
    "PAR_ADS_DOOR_OPEN_DEBOUNCE_TIME_XNF": "0B",
}


