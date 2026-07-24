---
mode: confluence-documentador
description: Cria uma página nova no espaço editável do Confluence a partir de um rascunho em drafts/.
---
Espaço (deve ser o de escrita): ${input:espaco:space key com mode "write" em config/spaces.json}
Rascunho: ${input:rascunho:caminho do arquivo em drafts/, ex. drafts/visao-geral.md}
Título: ${input:titulo:título final da página}
Página-pai (opcional): ${input:pai:ID da página-pai no Confluence, ou deixe em branco}

1. Confirme com o usuário o conteúdo final do rascunho antes de publicar.
2. Rode:
   `python scripts/publish.py create --space ${input:espaco} --title "${input:titulo}" --file ${input:rascunho}`
   (adicione `--ancestor-id ${input:pai}` se foi informado).
3. O script recusa sozinho se o espaço não estiver marcado `"mode": "write"`
   — se isso acontecer, avise o usuário em vez de tentar contornar.
4. Depois de criar, a página entra automaticamente em
   `.ai-managed-pages.json` — não edite esse arquivo manualmente.
5. Informe a URL da página criada ao usuário.
