import os
import pandas as pd
import binascii


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
