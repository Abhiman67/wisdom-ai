import json

input_file = "Bhagwad_Gita.jsonl"
output_file = "web/lib/gitaData.ts"

verses = []

try:
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            # Minimize size: keep only essential fields
            verses.append({
                "id": f"{item['metadata']['chapter']}.{item['metadata']['verse']}",
                "text": f"Chapter {item['metadata']['chapter']} Verse {item['metadata']['verse']}: {item['output']}",
                "sanskrit": item['input']
            })

    # Write as TS export
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("export const ALL_VERSES = ")
        json.dump(verses, f, ensure_ascii=False)
        f.write(";\n")
    
    print(f"✅ Created {output_file} with {len(verses)} verses.")

except Exception as e:
    print(f"❌ Error: {e}")
