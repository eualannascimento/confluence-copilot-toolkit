"""Front matter simétrico usado nos `content.md` gerados por extract.py e lido
de volta pelos rascunhos em publish.py — uma única implementação de
serialização/parsing para os dois lados não divergirem."""

from __future__ import annotations

import json


def dump(fields: dict) -> str:
    lines = "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in fields.items())
    return f"---\n{lines}\n---\n\n"


def parse(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    front, body = parts[1], parts[2]
    meta: dict = {}
    for line in front.strip().splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        try:
            meta[key.strip()] = json.loads(value.strip())
        except json.JSONDecodeError:
            meta[key.strip()] = value.strip()
    return meta, body.lstrip("\n")
