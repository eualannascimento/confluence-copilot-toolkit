#!/usr/bin/env python3
"""Extrai um espaço do Confluence para Markdown local, com índice.

Uso básico (extrai o espaço inteiro, ou só o que mudou desde a última vez):
    python scripts/extract.py --space MEUESPACO

Para espaços grandes, extrair tudo de uma vez pode demorar muito ou esbarrar
em limites do servidor on-premise. Formas de baixar em pedaços menores:

    python scripts/extract.py --space MEUESPACO --parent-id 123456   # só uma subárvore
    python scripts/extract.py --space MEUESPACO --label roadmap      # só páginas com essa label
    python scripts/extract.py --space MEUESPACO --since 2026-07-01   # só páginas alteradas depois dessa data
    python scripts/extract.py --space MEUESPACO --page-size 20       # lotes menores por requisição

Reextrair o mesmo espaço sem `--parent-id`/`--label`/`--since` é incremental
por padrão: só busca páginas modificadas desde a extração anterior (lida do
`_index.json` já existente) e mantém intactas as páginas não alteradas — não
refaz o trabalho todo a cada rodada. Use `--full` para forçar uma extração
completa mesmo já havendo uma extração anterior.

Se a extração for interrompida (Ctrl+C, queda de rede, VPN caindo), o
progresso feito até ali não se perde: os índices são regravados com as
páginas concluídas antes de sair, e a próxima rodada (incremental, por
padrão) completa o restante.

Gera, a partir da raiz do repositório:
    extracted/MEUESPACO/_index.json
    extracted/MEUESPACO/_index.md
    extracted/MEUESPACO/<slug-da-pagina>/content.md
    extracted/MEUESPACO/<slug-da-pagina>/meta.json

Não baixa anexos (por design — eles pesam demais). Cada anexo vira um link
direto de download quando a API expõe um, ou uma nota apontando a página
original quando não expõe.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import front_matter
from confluence_client import ConfluenceClient, ConfluenceConfigError, repo_root, write_json
from html_to_markdown import convert


def slugify(title: str, used: set[str], fallback_id: str) -> str:
    normalized = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    slug = slug[:80] or f"pagina-{fallback_id}"
    candidate = slug
    n = 2
    while candidate in used:
        candidate = f"{slug}-{n}"
        n += 1
    used.add(candidate)
    return candidate


def attachment_url_map(client: ConfluenceClient, page: dict) -> tuple[dict[str, str], int]:
    # Usa o lote de anexos já embutido em `page` (via expand=children.attachment)
    # sempre que possível — só cai numa chamada de API por página quando o
    # próprio Confluence sinaliza que a página tem mais anexos do que o lote
    # embutido trouxe (ver ConfluenceClient.page_attachments).
    attachments = client.page_attachments(page)
    mapping: dict[str, str] = {}
    for att in attachments:
        filename = att.get("title", "")
        download_path = att.get("_links", {}).get("download")
        if download_path:
            mapping[filename] = client.page_url(download_path)
    return mapping, len(attachments)


def load_existing_index(space_dir: Path) -> dict | None:
    index_path = space_dir / "_index.json"
    if not index_path.exists():
        return None
    return json.loads(index_path.read_text(encoding="utf-8"))


def to_cql_date(iso_timestamp: str) -> str:
    dt = datetime.fromisoformat(iso_timestamp)
    return dt.strftime("%Y-%m-%d %H:%M")


def write_indexes(space_dir: Path, space_key: str, index_entries: list[dict]) -> None:
    write_json(
        space_dir / "_index.json",
        {
            "space": space_key,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "page_count": len(index_entries),
            "pages": index_entries,
        },
    )

    lines = [f"# Índice — espaço {space_key}", "", f"{len(index_entries)} página(s).", ""]
    for entry in sorted(index_entries, key=lambda e: (len(e["ancestors"]), e["title"])):
        depth = len(entry["ancestors"])
        prefix = "  " * depth + "- "
        tag = f" `[{entry['attachment_count']} anexo(s)]`" if entry["attachment_count"] else ""
        lines.append(f"{prefix}[{entry['title']}]({entry['path']}){tag}")
    (space_dir / "_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--space", required=True, help="Space key do Confluence (ex.: ENG, PROJX)")
    parser.add_argument("--out", default=None, help="Pasta de saída (default: <raiz>/extracted)")
    parser.add_argument("--parent-id", default=None, help="Extrai só a subárvore a partir desta página")
    parser.add_argument("--label", default=None, help="Extrai só páginas com esta label")
    parser.add_argument("--since", default=None, help='Extrai só páginas alteradas a partir desta data ("YYYY-MM-DD")')
    parser.add_argument("--full", action="store_true", help="Força extração completa, ignorando o modo incremental")
    parser.add_argument("--page-size", type=int, default=50, help="Páginas por requisição à API (default: 50)")
    args = parser.parse_args()

    try:
        client = ConfluenceClient.from_env()
    except ConfluenceConfigError as exc:
        print(f"Erro de configuração: {exc}", file=sys.stderr)
        return 1

    space_key = args.space
    out_root = Path(args.out) if args.out else repo_root() / "extracted"
    space_dir = out_root / space_key
    space_dir.mkdir(parents=True, exist_ok=True)

    # O índice existente é sempre carregado como base de mescla (para não perder
    # do índice local páginas já extraídas fora do escopo desta rodada) e para
    # reaproveitar slugs/links já resolvidos. `--full`/escopo só afetam se ele
    # também é usado para auto-derivar o filtro `--since`.
    scoped = bool(args.parent_id or args.label)
    existing = load_existing_index(space_dir)

    since = args.since
    if since is None and existing is not None and not args.full and not scoped:
        since = to_cql_date(existing["extracted_at"])
        print(f"Extração incremental: só páginas alteradas desde {since} (use --full para forçar tudo).")

    existing_by_id: dict[str, dict] = {e["id"]: e for e in (existing["pages"] if existing else [])}
    used_slugs: set[str] = {e["path"].split("/")[0] for e in existing_by_id.values()}

    # Mapa de título -> caminho para resolver links internos, incluindo páginas
    # já extraídas em rodadas anteriores (não só o lote desta rodada).
    title_to_path: dict[str, str] = {
        f"{space_key}::{e['title']}": e["path"] for e in existing_by_id.values()
    }

    new_entries_by_id: dict[str, dict] = {}
    interrupted = False
    total = 0
    print(f"Buscando páginas do espaço {space_key}...")
    try:
        # Busca e conversão dentro do mesmo bloco protegido: uma interrupção
        # (Ctrl+C, VPN caindo) durante a paginação inicial ou durante a
        # conversão de uma página específica ainda preserva o que já foi
        # processado — nunca perde o trabalho de uma rodada inteira.
        for page in client.iter_space_pages(
            space_key,
            parent_id=args.parent_id,
            label=args.label,
            modified_since=since,
            page_size=args.page_size,
        ):
            total += 1
            existing_entry = existing_by_id.get(page["id"])
            slug = (
                existing_entry["path"].split("/")[0]
                if existing_entry
                else slugify(page["title"], used_slugs, page["id"])
            )
            rel_path = f"{slug}/content.md"
            title_to_path[f"{space_key}::{page['title']}"] = rel_path

            page_id = page["id"]
            title = page["title"]
            print(f"  [{total}] {title}")
            ancestors = page.get("ancestors", [])
            version = page.get("version", {}).get("number")
            labels = [
                lbl.get("name")
                for lbl in page.get("metadata", {}).get("labels", {}).get("results", [])
            ]
            webui = page.get("_links", {}).get("webui", "")
            page_url = client.page_url(webui) if webui else ""

            attachment_urls, attachment_count = attachment_url_map(client, page)

            storage_html = page.get("body", {}).get("storage", {}).get("value", "")
            body_md = convert(
                storage_html,
                space_key=space_key,
                page_title_to_path=title_to_path,
                attachment_url_by_filename=attachment_urls,
            )

            page_dir = space_dir / slug
            page_dir.mkdir(parents=True, exist_ok=True)

            front = front_matter.dump(
                {
                    "title": title,
                    "confluence_id": page_id,
                    "space": space_key,
                    "url": page_url,
                    "version": version,
                }
            )
            (page_dir / "content.md").write_text(front + body_md, encoding="utf-8")

            meta = {
                "id": page_id,
                "title": title,
                "space": space_key,
                "url": page_url,
                "version": version,
                "ancestors": [{"id": a["id"], "title": a["title"]} for a in ancestors],
                "labels": labels,
                "attachment_count": attachment_count,
                "attachments": [
                    {"filename": name, "url": url} for name, url in attachment_urls.items()
                ],
                "extracted_at": datetime.now(timezone.utc).isoformat(),
            }
            write_json(page_dir / "meta.json", meta)

            new_entries_by_id[page_id] = {
                "id": page_id,
                "title": title,
                "path": rel_path,
                "ancestors": [a["title"] for a in ancestors],
                "url": page_url,
                "version": version,
                "labels": labels,
                "attachment_count": attachment_count,
            }
    except KeyboardInterrupt:
        interrupted = True
        print(
            f"\nInterrompido em {len(new_entries_by_id)}/{total} páginas. "
            "Gravando o progresso feito até aqui antes de sair...",
            file=sys.stderr,
        )

    merged = {**existing_by_id, **new_entries_by_id}
    write_indexes(space_dir, space_key, list(merged.values()))

    if interrupted:
        print(
            f"Progresso salvo: {len(new_entries_by_id)} página(s) desta rodada + "
            f"{len(existing_by_id)} já extraídas antes = {len(merged)} no total. "
            "Rode o mesmo comando de novo para completar o restante (modo incremental)."
        )
        return 130

    print(f"Concluído: {len(merged)} página(s) no total em {space_dir}")
    print("Rode 'python scripts/build_global_index.py' para atualizar o índice global.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
