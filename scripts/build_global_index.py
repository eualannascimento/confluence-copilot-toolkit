#!/usr/bin/env python3
"""Gera extracted/GLOBAL_INDEX.md a partir dos _index.json já existentes.

Não chama a API do Confluence — só varre o que já foi extraído. Pensado para
ser o primeiro arquivo que a IA lê antes de abrir qualquer conteúdo: uma
tabela barata (poucos tokens) que diz o que existe e onde, para ela decidir
o que vale a pena abrir de fato.

Uso:
    python scripts/build_global_index.py
"""

from __future__ import annotations

import json

from confluence_client import load_spaces_config, repo_root


def main() -> int:
    extracted_dir = repo_root() / "extracted"
    extracted_dir.mkdir(parents=True, exist_ok=True)
    modes = load_spaces_config()

    rows = []
    for index_file in sorted(extracted_dir.glob("*/_index.json")):
        data = json.loads(index_file.read_text(encoding="utf-8"))
        space_key = data["space"]
        rows.append(
            {
                "space": space_key,
                "mode": modes.get(space_key, "?"),
                "page_count": data["page_count"],
                "extracted_at": data["extracted_at"],
                "path": f"{space_key}/_index.md",
            }
        )

    lines = [
        "# Índice global — espaços extraídos do Confluence",
        "",
        "Leia este arquivo primeiro. Para navegar dentro de um espaço, abra o",
        "`_index.md` dele (coluna Índice) antes de abrir páginas individuais.",
        "",
        "| Espaço | Modo | Páginas | Última extração | Índice |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['space']} | {row['mode']} | {row['page_count']} | "
            f"{row['extracted_at']} | [{row['path']}]({row['path']}) |"
        )
    if not rows:
        lines.append("| _nenhum espaço extraído ainda_ | | | | |")

    (extracted_dir / "GLOBAL_INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"GLOBAL_INDEX.md atualizado com {len(rows)} espaço(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
