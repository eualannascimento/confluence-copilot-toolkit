"""Cliente HTTP mínimo para Confluence Server/Data Center (REST API v1).

Não depende de nenhuma IA — só requests + stdlib. Suporta os dois modos de
autenticação possíveis num Confluence on-premise:

- Personal Access Token (Bearer), se o admin tiver habilitado PATs.
- Usuário/senha (Basic Auth), como fallback quase certo em instâncias antigas.

A senha nunca é gravada em arquivo em texto puro. Se `keyring` estiver
disponível, ela é salva no cofre de credenciais do sistema operacional
(Windows Credential Manager, macOS Keychain) na primeira vez, e reaproveitada
nas próximas execuções. Caso contrário, é pedida via `getpass` a cada rodada.
"""

from __future__ import annotations

import getpass
import json
import os
from pathlib import Path
from typing import Any, Iterator

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dotenv é opcional em runtime mínimo
    load_dotenv = None

try:
    import keyring
    import keyring.errors
except ImportError:  # pragma: no cover - keyring é opcional
    keyring = None

KEYRING_SERVICE = "confluence-copilot-toolkit"


def repo_root() -> Path:
    """Raiz do repositório real (pasta que contém scripts/, config/, extracted/)."""
    return Path(__file__).resolve().parent.parent


def load_config() -> None:
    """Carrega config/.env, se existir, sem sobrescrever variáveis já setadas."""
    if load_dotenv is None:
        return
    env_path = repo_root() / "config" / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)


def load_spaces_config() -> dict[str, str]:
    """Lê config/spaces.json (se existir): {space_key: "read"|"write"}."""
    path = repo_root() / "config" / "spaces.json"
    if not path.exists():
        return {}
    entries = json.loads(path.read_text(encoding="utf-8"))
    return {e["key"]: e.get("mode", "read") for e in entries}


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class ConfluenceConfigError(RuntimeError):
    pass


class ConfluenceClient:
    def __init__(self, base_url: str, session: requests.Session):
        self.base_url = base_url.rstrip("/")
        self.session = session

    # -- construção --------------------------------------------------

    @classmethod
    def from_env(cls) -> "ConfluenceClient":
        load_config()

        base_url = os.environ.get("CONFLUENCE_BASE_URL")
        if not base_url:
            raise ConfluenceConfigError(
                "CONFLUENCE_BASE_URL não definida. Copie config/.env.example para "
                "config/.env e preencha, ou exporte a variável antes de rodar."
            )

        auth_mode = os.environ.get("CONFLUENCE_AUTH_MODE", "basic").strip().lower()
        session = requests.Session()
        session.headers["Accept"] = "application/json"
        retry = Retry(
            total=4,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            # allowed_methods no default (GET/HEAD/PUT/OPTIONS/DELETE/TRACE) — de propósito
            # NÃO inclui POST, para nunca repetir `create_page` sozinho e duplicar página.
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        if auth_mode == "pat":
            token = os.environ.get("CONFLUENCE_PAT")
            if not token:
                token = getpass.getpass(
                    "Personal Access Token do Confluence (não fica visível ao digitar): "
                )
            session.headers["Authorization"] = f"Bearer {token}"

        elif auth_mode == "basic":
            user = os.environ.get("CONFLUENCE_USER")
            if not user:
                user = input("Usuário do Confluence: ").strip()

            password = os.environ.get("CONFLUENCE_PASSWORD")
            if not password and keyring is not None:
                password = keyring.get_password(KEYRING_SERVICE, user)

            if not password:
                password = getpass.getpass(f"Senha do Confluence ({user}): ")
                if keyring is not None:
                    try:
                        keyring.set_password(KEYRING_SERVICE, user, password)
                    except keyring.errors.KeyringError:
                        # Sem cofre de credenciais disponível no SO — segue sem persistir.
                        pass

            session.auth = (user, password)

        else:
            raise ConfluenceConfigError(
                f"CONFLUENCE_AUTH_MODE inválido: {auth_mode!r}. Use 'pat' ou 'basic'."
            )

        return cls(base_url, session)

    # -- HTTP genérico -------------------------------------------------

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        # Retry/backoff para 429/5xx já configurado no adapter da sessão (from_env).
        url = path if path.startswith("http") else f"{self.base_url}{path}"
        return self.session.request(method, url, timeout=30, **kwargs)

    def get(self, path: str, params: dict | None = None) -> dict:
        resp = self._request("GET", path, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_paginated(self, path: str, params: dict | None = None) -> Iterator[dict]:
        """Itera por todas as páginas de resultado (segue `_links.next`)."""
        params = dict(params or {})
        params.setdefault("limit", 50)
        next_path = path
        next_params: dict | None = params
        while next_path:
            data = self.get(next_path, params=next_params)
            for item in data.get("results", []):
                yield item
            next_link = data.get("_links", {}).get("next")
            if not next_link:
                break
            next_path = next_link
            next_params = None  # já vem com query string embutida

    def post(self, path: str, json_body: dict) -> dict:
        resp = self._request("POST", path, json=json_body)
        resp.raise_for_status()
        return resp.json()

    def put(self, path: str, json_body: dict) -> dict:
        resp = self._request("PUT", path, json=json_body)
        resp.raise_for_status()
        return resp.json()

    # -- operações de conteúdo -----------------------------------------

    def iter_space_pages(
        self,
        space_key: str,
        *,
        parent_id: str | None = None,
        label: str | None = None,
        modified_since: str | None = None,
        page_size: int = 50,
    ) -> Iterator[dict]:
        """Itera páginas do espaço, com filtros CQL opcionais para extrair em
        pedaços em vez do espaço inteiro de uma vez (subárvore, label, ou só
        o que mudou desde uma data — `modified_since` no formato "YYYY-MM-DD
        HH:mm" ou "YYYY-MM-DD").
        """
        # children.attachment vem embutido na mesma chamada — evita 1 request de
        # anexos por página (N+1). Só cai para get_attachments() se a página tiver
        # mais anexos do que o lote embutido trouxe (ver extract.py).
        expand = "body.storage,ancestors,version,space,metadata.labels,children.attachment"

        clauses = [f'space="{space_key}"', "type=page"]
        if parent_id:
            clauses.append(f"ancestor={parent_id}")
        if label:
            clauses.append(f'label="{label}"')
        if modified_since:
            clauses.append(f'lastmodified >= "{modified_since}"')
        cql = " and ".join(clauses)

        yield from self.get_paginated(
            "/rest/api/content/search",
            params={"cql": cql, "expand": expand, "limit": page_size},
        )

    def get_attachments(self, page_id: str) -> list[dict]:
        return list(
            self.get_paginated(f"/rest/api/content/{page_id}/child/attachment")
        )

    def page_attachments(self, page: dict) -> list[dict]:
        """Anexos de uma página já listada por iter_space_pages.

        Usa o lote embutido via `children.attachment` (sem chamada de rede
        extra); só busca a lista completa via API se o lote embutido não
        cobrir todos os anexos da página (`_links.next` presente).
        """
        children = page.get("children", {}).get("attachment", {})
        if children.get("_links", {}).get("next"):
            return self.get_attachments(page["id"])
        return children.get("results", [])

    def get_page(self, page_id: str, expand: str = "version") -> dict:
        return self.get(f"/rest/api/content/{page_id}", params={"expand": expand})

    def create_page(
        self, space_key: str, title: str, storage_html: str, ancestor_id: str | None = None
    ) -> dict:
        body = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {"storage": {"value": storage_html, "representation": "storage"}},
        }
        if ancestor_id:
            body["ancestors"] = [{"id": ancestor_id}]
        return self.post("/rest/api/content", body)

    def update_page(self, page_id: str, title: str, storage_html: str, version_number: int) -> dict:
        body = {
            "id": page_id,
            "type": "page",
            "title": title,
            "body": {"storage": {"value": storage_html, "representation": "storage"}},
            "version": {"number": version_number},
        }
        return self.put(f"/rest/api/content/{page_id}", body)

    def page_url(self, webui_path: str) -> str:
        return f"{self.base_url}{webui_path}"
