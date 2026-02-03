r"""
Convert `Bhagwad_Gita.csv` -> JSONL suitable for instruction-tuning.
Adjust COLUMN_* variables below if your CSV column names differ.
Example output format per line:
    {"instruction": "Explain the meaning of the following verse in simple English.", "input": "<Shloka>\n<Transliteration>", "output": "<EngMeaning>", "metadata": {...}}

Run (PowerShell):
    python .\convert_csv_to_jsonl.py "C:\\Users\\shash\\Downloads\\Bhagwad_Gita.csv" --out .\Bhagwad_Gita.jsonl

"""
import csv
import json
import argparse
from pathlib import Path
# Default column names observed in your CSV. Change if different.
COLUMN_ID = "ID"
COLUMN_CHAPTER = "Chapter"
COLUMN_VERSE = "Verse"
COLUMN_SHLOKA = "Shloka"
COLUMN_TRANSLIT = "Transliteration"
COLUMN_ENG = "EngMeaning"

DEFAULT_INSTRUCTION = "Explain the meaning of the following Bhagavad Gita verse in simple, modern English. Keep the explanation concise (2-4 sentences) and mention any key context if relevant."

parser = argparse.ArgumentParser(description="Convert Bhagavad Gita CSV to JSONL for instruction tuning.")
parser.add_argument("csv", help="Path to source CSV")
parser.add_argument("--out", default=None, help="Path to output JSONL file")
parser.add_argument("--instruction", default=DEFAULT_INSTRUCTION, help="Instruction text to use for each example")
parser.add_argument("--max_rows", type=int, default=None, help="If set, only process this many rows (for testing)")
args = parser.parse_args()

csv_path = Path(args.csv)
if args.out:
    out_path = Path(args.out)
else:
    out_path = csv_path.with_suffix('.jsonl')

rows_written = 0
with csv_path.open(encoding='utf-8', errors='replace') as f_in, out_path.open('w', encoding='utf-8') as f_out:
    reader = csv.DictReader(f_in)
    for i, row in enumerate(reader):
        if args.max_rows and i >= args.max_rows:
            break

        # Safely pull fields; fall back to empty string when missing
        shloka = (row.get(COLUMN_SHLOKA) or '').strip()
        translit = (row.get(COLUMN_TRANSLIT) or '').strip()
        eng = (row.get(COLUMN_ENG) or '').strip()

        if not eng:
            # If no English meaning available, skip or use Hindi column if you want (not enabled by default)
            continue

        # Build input text: include original shloka and transliteration if present
        input_parts = []
        if shloka:
            input_parts.append("Original (Sanskrit):\n" + shloka)
        if translit:
            input_parts.append("Transliteration:\n" + translit)
        input_text = "\n\n".join(input_parts)

        obj = {
            "instruction": args.instruction,
            "input": input_text,
            "output": eng,
            "metadata": {
                "source_file": str(csv_path.name),
                "row_id": row.get(COLUMN_ID, ''),
                "chapter": row.get(COLUMN_CHAPTER, ''),
                "verse": row.get(COLUMN_VERSE, '')
            }
        }

        f_out.write(json.dumps(obj, ensure_ascii=False) + "\n")
        rows_written += 1

print(f"Wrote {rows_written} examples to: {out_path}")
