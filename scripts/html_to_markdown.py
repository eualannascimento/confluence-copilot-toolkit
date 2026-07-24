"""Converte o "storage format" do Confluence (XHTML + macros ac:/ri:) em Markdown.

Não é um conversor perfeito — cobre o que aparece na grande maioria das páginas
reais (parágrafos, títulos, listas, tabelas, links, negrito/itálico, blocos de
código, painéis de aviso, imagens/anexos, links internos entre páginas) e nunca
descarta conteúdo em silêncio: qualquer macro não reconhecida vira uma nota
visível em vez de desaparecer, para não violar a regra de nunca perder
informação na extração.
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup
from markdownify import markdownify as md

_PANEL_LABELS = {
    "info": "Nota",
    "note": "Observação",
    "warning": "Atenção",
    "tip": "Dica",
}

_BLANK_RUN_RE = re.compile(r"\n{4,}")


def _resolve_attachment(filename: str, attachment_map: dict[str, str], *, display: str, not_found: str) -> str:
    if filename and filename in attachment_map:
        return f"[{display}]({attachment_map[filename]})"
    return not_found


def convert(
    storage_html: str,
    *,
    space_key: str,
    page_title_to_path: dict[str, str] | None = None,
    attachment_url_by_filename: dict[str, str] | None = None,
) -> str:
    """Converte um corpo `body.storage.value` do Confluence em Markdown.

    - `page_title_to_path`: mapa `"SPACE::Título" -> caminho relativo do .md já
      extraído`, para resolver links internos entre páginas do mesmo lote de
      extração. Sem entrada correspondente, o link vira texto simples citando
      o título da página de destino (sem quebrar a leitura, sem inventar URL).
    - `attachment_url_by_filename`: mapa `nome-do-arquivo -> URL de download`,
      construído a partir da resposta da API de anexos daquela página.
    """
    page_title_to_path = page_title_to_path or {}
    attachment_url_by_filename = attachment_url_by_filename or {}

    soup = BeautifulSoup(storage_html or "", "html.parser")

    blocks: list[str] = []

    def stash(markdown_chunk: str) -> str:
        blocks.append(markdown_chunk)
        return f"CFBLOCKPLACEHOLDERxyz{len(blocks) - 1}xyz"

    # Um único find_all cobre as três construções ac:* que precisam de
    # tratamento especial — evita três varreduras separadas da mesma árvore.
    for tag in soup.find_all(["ac:structured-macro", "ac:image", "ac:link"]):
        if tag.name == "ac:structured-macro":
            _convert_macro(tag, stash)
        elif tag.name == "ac:image":
            _convert_image(tag, stash, attachment_url_by_filename)
        else:
            _convert_link(tag, stash, space_key, page_title_to_path, attachment_url_by_filename)

    markdown_text = md(str(soup), heading_style="ATX")

    for i, chunk in enumerate(blocks):
        markdown_text = markdown_text.replace(f"CFBLOCKPLACEHOLDERxyz{i}xyz", chunk)

    markdown_text = _BLANK_RUN_RE.sub("\n\n\n", markdown_text)
    return markdown_text.strip() + "\n"


def _convert_macro(macro, stash) -> None:
    name = macro.get("ac:name", "")

    if name == "code":
        lang = ""
        for param in macro.find_all("ac:parameter"):
            if param.get("ac:name") == "language":
                lang = param.get_text(strip=True)
        body_tag = macro.find("ac:plain-text-body")
        code_text = body_tag.get_text() if body_tag else macro.get_text()
        placeholder = stash(f"\n```{lang}\n{code_text.rstrip(chr(10))}\n```\n")

    elif name in _PANEL_LABELS:
        body_tag = macro.find("ac:rich-text-body")
        inner_md = md(str(body_tag)) if body_tag else ""
        label = _PANEL_LABELS[name]
        quoted = "\n".join(f"> {line}" for line in inner_md.strip().splitlines())
        placeholder = stash(f"\n> **{label}:**\n{quoted}\n")

    elif name == "toc":
        # Redundante com o índice gerado pelo extrator — removido sem perda
        # de informação (a hierarquia real vive em _index.md/_index.json).
        macro.decompose()
        return

    else:
        placeholder = stash(
            f"\n> _[macro Confluence não convertida automaticamente: `{name}` — ver página original]_\n"
        )

    macro.replace_with(placeholder)


def _convert_image(image, stash, attachment_url_by_filename: dict[str, str]) -> None:
    ri_attachment = image.find("ri:attachment")
    filename = ri_attachment.get("ri:filename") if ri_attachment is not None else None
    ri_url = image.find("ri:url")
    external_url = ri_url.get("ri:value") if ri_url is not None else None

    if filename:
        placeholder = stash(
            _resolve_attachment(
                filename,
                attachment_url_by_filename,
                display=f"Anexo: {filename}",
                not_found=f"> Anexo referenciado nesta página (link não resolvido automaticamente): {filename}",
            )
        )
    elif external_url:
        placeholder = stash(f"![imagem externa]({external_url})")
    else:
        placeholder = stash("> Imagem referenciada nesta página (origem não identificada)")
    image.replace_with(placeholder)


def _convert_link(link, stash, space_key: str, page_title_to_path: dict[str, str], attachment_url_by_filename: dict[str, str]) -> None:
    ri_page = link.find("ri:page")
    ri_attachment = link.find("ri:attachment")
    text_body = link.find("ac:plain-text-link-body")
    link_text = text_body.get_text() if text_body else None

    if ri_page is not None:
        target_title = ri_page.get("ri:content-title", "")
        target_space = ri_page.get("ri:space-key", space_key)
        key = f"{target_space}::{target_title}"
        display = link_text or target_title
        if key in page_title_to_path:
            placeholder = stash(f"[{display}]({page_title_to_path[key]})")
        else:
            placeholder = stash(
                f"[{display}]() _(página do Confluence: \"{target_title}\", espaço {target_space} — não incluída nesta extração)_"
            )
    elif ri_attachment is not None:
        filename = ri_attachment.get("ri:filename", "")
        display = link_text or filename
        placeholder = stash(
            _resolve_attachment(
                filename,
                attachment_url_by_filename,
                display=display,
                not_found=f"[{display}] _(anexo: {filename})_",
            )
        )
    else:
        placeholder = stash(link_text or "")
    link.replace_with(placeholder)
