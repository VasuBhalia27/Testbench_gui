"""
Utility: Merge multiple CSV files into single Excel workbook with one sheet per CSV.

Usage:
  python merge_csvs_to_xlsx.py <input_folder> <output_xlsx_path>

The script prefers pandas if available, otherwise falls back to csv + openpyxl.
"""
import sys
from pathlib import Path


def merge_with_pandas(csv_paths, out_path):
    import pandas as pd
    from openpyxl import Workbook

    with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
        for p in csv_paths:
            name = p.stem
            try:
                df = pd.read_csv(p, encoding='utf-8-sig')
            except Exception:
                df = pd.read_csv(p)
            df.to_excel(writer, sheet_name=name[:31], index=False)


def merge_with_csv(csv_paths, out_path):
    from openpyxl import Workbook
    import csv

    wb = Workbook()
    # remove default sheet
    default = wb.active
    wb.remove(default)

    for p in csv_paths:
        name = p.stem[:31]
        ws = wb.create_sheet(title=name)
        with p.open('r', encoding='utf-8-sig', errors='replace') as fh:
            reader = csv.reader(fh)
            for r_idx, row in enumerate(reader, start=1):
                ws.append(row)

    wb.save(out_path)


def main():
    if len(sys.argv) < 3:
        print("Usage: python merge_csvs_to_xlsx.py <input_folder> <output_xlsx_path> [sheet_order_comma_separated]")
        sys.exit(2)

    input_folder = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    # Optional third arg: comma-separated preferred sheet order (by CSV stem)
    preferred_order = []
    if len(sys.argv) >= 4:
        preferred_order = [s.strip().lower() for s in sys.argv[3].split(',') if s.strip()]

    if not input_folder.exists():
        print(f"Input folder does not exist: {input_folder}")
        sys.exit(2)

    csv_paths = list(input_folder.glob('*.csv'))
    # Normalize discovered CSVs by stem -> Path
    stem_map = {p.stem.lower(): p for p in csv_paths}

    ordered_paths = []
    # If a preferred order was provided, place those first in that order
    if preferred_order:
        for name in preferred_order:
            p = stem_map.get(name)
            if p:
                ordered_paths.append(p)
                stem_map.pop(name, None)

    # Default fallback order based on common template (match screenshot)
    default_order = [
        'voltage_check', 'led', 'battery', 'motor', 'eos', 'sg', 'capa', 'nfc', 'can', 'lin'
    ]
    # Fill remaining according to default_order if they exist and not already added
    for name in default_order:
        p = stem_map.get(name)
        if p and p not in ordered_paths:
            ordered_paths.append(p)
            stem_map.pop(name, None)

    # Append any remaining CSVs (alphabetical)
    remaining = sorted(stem_map.values(), key=lambda x: x.name.lower())
    ordered_paths.extend(remaining)

    csv_paths = ordered_paths
    if not csv_paths:
        print(f"No CSV files found in {input_folder}")
        sys.exit(2)

    try:
        # Prefer pandas
        import pandas as pd  # type: ignore
        merge_with_pandas(csv_paths, out_path)
    except Exception:
        merge_with_csv(csv_paths, out_path)

    print(f"Merged {len(csv_paths)} CSV(s) into {out_path}")


if __name__ == '__main__':
    main()
