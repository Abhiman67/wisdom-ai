import csv, json, argparse, os

DEF_INSTRUCTION = "Answer the question concisely about the Bhagavad Gita."  # Keep consistent with earlier 800-sample dataset

def convert(csv_path: str, out_path: str, limit: int | None = None):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    count = 0
    with open(csv_path, newline='', encoding='utf-8') as f_in, open(out_path, 'w', encoding='utf-8') as f_out:
        reader = csv.DictReader(f_in)
        for row in reader:
            if limit is not None and count >= limit:
                break
            q = (row.get('question') or '').strip()
            a = (row.get('answer') or '').strip()
            if not q or not a:
                # Skip malformed rows quietly
                continue
            obj = {
                "instruction": DEF_INSTRUCTION,
                "input": q,
                "output": a,
                "metadata": {
                    "chapter": row.get('chapter_no'),
                    "verse": row.get('verse_no')
                }
            }
            f_out.write(json.dumps(obj, ensure_ascii=False) + "\n")
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description="Convert english.csv to JSONL for LoRA fine-tuning.")
    parser.add_argument('--csv', default='english.csv', help='Input CSV file path.')
    parser.add_argument('--out', default='english_full.jsonl', help='Output JSONL file path.')
    parser.add_argument('--limit', type=int, default=None, help='Optional max number of rows to convert.')
    args = parser.parse_args()
    rows = convert(args.csv, args.out, args.limit)
    print(f"Wrote {rows} JSONL lines to {args.out}")

if __name__ == '__main__':
    main()
