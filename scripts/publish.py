#!/usr/bin/env python3
"""Publica páginas no espaço editável do Confluence — create ou update.

Regras de segurança, aplicadas no próprio código (não só por convenção) —
ambas vivem em `registry.guarded_create`/`guarded_update`, o único caminho
autorizado de escrita usado por este script:

- `update` só funciona se o `--page-id` já estiver em `.ai-managed-pages.json`
  (ou seja, se a própria IA/este toolkit criou a página). Página que já
  existia antes no Confluence e nunca passou por `create` aqui não pode ser
  atualizada por este script.
- Não existe comando de exclusão. Não há função de delete neste arquivo nem
  em `registry.py`/`confluence_client.py`.
- `create` só é permitido em espaços marcados `"mode": "write"` em
  `config/spaces.json`.

Uso:
    python scripts/publish.py create --space MEUESPACO --title "Título da página" --file drafts/minha-pagina.md [--ancestor-id 12345]
    python scripts/publish.py update --page-id 98765 --file drafts/minha-pagina.md
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

import markdown as md_lib

import front_matter
import registry
from confluence_client import ConfluenceClient, ConfluenceConfigError, repo_root

_CODE_BLOCK_RE = re.compile(
    r'<pre><code(?: class="language-(?P<lang>[\w+-]*)")?>(?P<code>.*?)</code></pre>',
    re.DOTALL,
)


def markdown_to_storage(markdown_text: str) -> str:
    html_body = md_lib.markdown(markdown_text, extensions=["tables", "fenced_code"])

    def to_code_macro(match: re.Match) -> str:
        lang = match.group("lang") or ""
        code = html.unescape(match.group("code"))
        return (
            '<ac:structured-macro ac:name="code">'
            f'<ac:parameter ac:name="language">{lang}</ac:parameter>'
            f"<ac:plain-text-body><![CDATA[{code}]]></ac:plain-text-body>"
            "</ac:structured-macro>"
        )

    return _CODE_BLOCK_RE.sub(to_code_macro, html_body)


def _load_draft(file_arg: str) -> tuple[dict, str, Path]:
    draft_path = Path(file_arg)
    if not draft_path.is_absolute():
        draft_path = repo_root() / draft_path
    if not draft_path.exists():
        raise FileNotFoundError(f"Arquivo de rascunho não encontrado: {draft_path}")
    meta, body = front_matter.parse(draft_path.read_text(encoding="utf-8"))
    return meta, body, draft_path


def _client_or_none() -> ConfluenceClient | None:
    try:
        return ConfluenceClient.from_env()
    except ConfluenceConfigError as exc:
        print(f"Erro de configuração: {exc}", file=sys.stderr)
        return None


def cmd_create(args: argparse.Namespace) -> int:
    try:
        meta, body, draft_path = _load_draft(args.file)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1

    title = args.title or meta.get("title")
    if not title:
        print("Título não informado (--title ou front matter 'title:' no rascunho).", file=sys.stderr)
        return 1

    client = _client_or_none()
    if client is None:
        return 1

    try:
        result = registry.guarded_create(
            client,
            space_key=args.space,
            title=title,
            storage_html=markdown_to_storage(body),
            draft_path=str(draft_path.relative_to(repo_root())),
            ancestor_id=args.ancestor_id,
        )
    except PermissionError as exc:
        print(exc, file=sys.stderr)
        return 1

    print(f"Página criada: {title} (id {result['id']})")
    webui = result.get("_links", {}).get("webui", "")
    if webui:
        print(f"URL: {client.page_url(webui)}")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    try:
        meta, body, _ = _load_draft(args.file)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1

    client = _client_or_none()
    if client is None:
        return 1

    entries = registry.load_registry()
    entry = registry.find_entry(entries, args.page_id)
    title = args.title or meta.get("title") or (entry["title"] if entry else None)
    if not title:
        print("Título não informado e não encontrado no registro.", file=sys.stderr)
        return 1

    try:
        _, next_version = registry.guarded_update(
            client, page_id=args.page_id, title=title, storage_html=markdown_to_storage(body)
        )
    except PermissionError as exc:
        print(exc, file=sys.stderr)
        return 1

    print(f"Página {args.page_id} atualizada para a versão {next_version}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="Cria uma página nova a partir de um rascunho Markdown")
    p_create.add_argument("--space", required=True)
    p_create.add_argument("--title", default=None)
    p_create.add_argument("--file", required=True, help="Caminho do rascunho .md (ex.: drafts/minha-pagina.md)")
    p_create.add_argument("--ancestor-id", default=None, help="ID da página-pai (opcional)")
    p_create.set_defaults(func=cmd_create)

    p_update = sub.add_parser("update", help="Atualiza uma página já criada por este toolkit")
    p_update.add_argument("--page-id", required=True)
    p_update.add_argument("--title", default=None)
    p_update.add_argument("--file", required=True)
    p_update.set_defaults(func=cmd_update)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
