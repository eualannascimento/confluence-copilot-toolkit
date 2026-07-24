"""Registro local de páginas gerenciadas pela IA (`.ai-managed-pages.json`)
e o único caminho autorizado para criar/atualizar página no Confluence.

É a fonte da verdade sobre quais páginas o toolkit tem permissão de
atualizar. Uma página só entra aqui quando é criada por `guarded_create` —
nunca é preenchida "na mão" para uma página que já existia antes.

`guarded_create`/`guarded_update` existem para que a trava de segurança viva
num único mecanismo compartilhado, não numa checagem solta em cada script
que chama a API — qualquer chamador (CLI, prompt, futuro script) deve passar
por aqui, em vez de reimplementar a checagem antes de chamar
`ConfluenceClient` diretamente.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from confluence_client import ConfluenceClient, load_spaces_config, repo_root, write_json

REGISTRY_FILENAME = ".ai-managed-pages.json"


def _registry_path() -> Path:
    return repo_root() / REGISTRY_FILENAME


def load_registry() -> list[dict]:
    path = _registry_path()
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_registry(entries: list[dict]) -> None:
    write_json(_registry_path(), entries)


def find_entry(entries: list[dict], page_id: str) -> dict | None:
    for entry in entries:
        if entry.get("confluence_page_id") == page_id:
            return entry
    return None


def register_new_page(*, page_id: str, space_key: str, title: str, draft_path: str) -> None:
    entries = load_registry()
    now = datetime.now(timezone.utc).isoformat()
    entries.append(
        {
            "confluence_page_id": page_id,
            "space_key": space_key,
            "title": title,
            "local_draft_path": draft_path,
            "created_at": now,
            "last_published_at": now,
        }
    )
    save_registry(entries)


def mark_republished(*, page_id: str) -> None:
    entries = load_registry()
    entry = find_entry(entries, page_id)
    if entry is None:
        raise ValueError(f"Página {page_id} não está no registro — nada a atualizar.")
    entry["last_published_at"] = datetime.now(timezone.utc).isoformat()
    save_registry(entries)


def guarded_create(
    client: ConfluenceClient,
    *,
    space_key: str,
    title: str,
    storage_html: str,
    draft_path: str,
    ancestor_id: str | None = None,
) -> dict:
    """Único caminho autorizado para criar página — valida o espaço antes de escrever."""
    modes = load_spaces_config()
    if modes.get(space_key) != "write":
        raise PermissionError(
            f"Espaço '{space_key}' não está marcado como 'write' em config/spaces.json. "
            "Recusando criar página por segurança."
        )
    result = client.create_page(space_key, title, storage_html, ancestor_id=ancestor_id)
    register_new_page(page_id=result["id"], space_key=space_key, title=title, draft_path=draft_path)
    return result


def guarded_update(client: ConfluenceClient, *, page_id: str, title: str, storage_html: str) -> tuple[dict, int]:
    """Único caminho autorizado para atualizar página — valida o registro antes de escrever."""
    entries = load_registry()
    if find_entry(entries, page_id) is None:
        raise PermissionError(
            f"Página {page_id} não está em {REGISTRY_FILENAME} — não foi criada por "
            "este toolkit. Edição recusada por segurança."
        )
    current = client.get_page(page_id, expand="version")
    next_version = current["version"]["number"] + 1
    result = client.update_page(page_id, title, storage_html, next_version)
    mark_republished(page_id=page_id)
    return result, next_version
