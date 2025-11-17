#!/usr/bin/env python3
"""Build sentence-transformers embeddings for passages and FAISS index.

Produces: <index_dir>/passages.faiss and passages_meta.jsonl
"""
import argparse
import json
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


def main(passages, index_dir, model_name="sentence-transformers/all-MiniLM-L6-v2"):
    os.makedirs(index_dir, exist_ok=True)
    model = SentenceTransformer(model_name)

    texts = []
    metas = []
    with open(passages, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            texts.append(obj["text"])
            metas.append({"id": obj["id"], "meta": obj.get("meta", {})})

    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    faiss.write_index(index, os.path.join(index_dir, "passages.faiss"))

    meta_path = os.path.join(index_dir, "passages_meta.jsonl")
    with open(meta_path, "w", encoding="utf-8") as mf:
        for m in metas:
            mf.write(json.dumps(m, ensure_ascii=False) + "\n")

    print("Index saved to", index_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--passages", required=True)
    parser.add_argument("--index_dir", default="data")
    parser.add_argument("--model_name", default="sentence-transformers/all-MiniLM-L6-v2")
    args = parser.parse_args()
    main(args.passages, args.index_dir, args.model_name)
