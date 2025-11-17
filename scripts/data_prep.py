#!/usr/bin/env python3
"""Prepare passages and small instruct-style JSONL for toy fine-tuning.

Input: CSV with columns like ID,Chapter,Verse,Shloka,Transliteration,EngMeaning,...
Outputs:
- data/passages.jsonl  -> {"id":..., "text":..., "meta":{...}}
- data/instruct.jsonl -> {"prompt":..., "completion":...}
"""
import argparse
import json
import os
import pandas as pd


def main(csv, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    df = pd.read_csv(csv)

    passages_path = os.path.join(out_dir, "passages.jsonl")
    instruct_path = os.path.join(out_dir, "instruct.jsonl")

    with open(passages_path, "w", encoding="utf-8") as p_f, open(instruct_path, "w", encoding="utf-8") as i_f:
        for _, row in df.iterrows():
            pid = row.get("ID") or f"vers-{row.get('Chapter')}-{row.get('Verse')}"
            shloka = row.get("Shloka") if not pd.isna(row.get("Shloka")) else ""
            eng = row.get("EngMeaning") if not pd.isna(row.get("EngMeaning")) else ""
            translit = row.get("Transliteration") if not pd.isna(row.get("Transliteration")) else ""

            text = "\n".join([s for s in [shloka, translit, eng] if s])
            meta = {"chapter": row.get("Chapter"), "verse": row.get("Verse")}

            p_f.write(json.dumps({"id": pid, "text": text, "meta": meta}, ensure_ascii=False) + "\n")

            # create a simple instruct pair: Q -> contextual verse explanation
            prompt = f"User: Explain the meaning of verse {pid} in simple words.\nContext:" \
                     f"\n{shloka if shloka else eng}\n---\nAnswer:"
            completion = eng or shloka
            i_f.write(json.dumps({"prompt": prompt, "completion": completion}, ensure_ascii=False) + "\n")

    print("Wrote:", passages_path, instruct_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out_dir", default="data")
    args = parser.parse_args()
    main(args.csv, args.out_dir)
