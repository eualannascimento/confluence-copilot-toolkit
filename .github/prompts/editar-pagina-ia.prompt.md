---
mode: confluence-documentador
description: Atualiza uma página do Confluence que foi criada por este toolkit (precisa estar em .ai-managed-pages.json).
---
ID da página no Confluence: ${input:pageId:confluence_page_id em .ai-managed-pages.json}
Rascunho atualizado: ${input:rascunho:caminho do arquivo em drafts/}

1. Confira em `.ai-managed-pages.json` se `${input:pageId}` está registrado.
   Se não estiver, **não prossiga** — explique ao usuário que essa página não
   foi criada por este toolkit e que a edição precisa ser feita direto no
   Confluence.
2. Confirme com o usuário o conteúdo final do rascunho antes de publicar.
3. Rode:
   `python scripts/publish.py update --page-id ${input:pageId} --file ${input:rascunho}`
4. Informe a nova versão da página e a URL ao usuário.
