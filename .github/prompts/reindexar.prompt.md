---
mode: confluence-documentador
description: Reconstrói extracted/GLOBAL_INDEX.md a partir do que já foi extraído, sem chamar a API do Confluence.
---
Rode `python scripts/build_global_index.py` e mostre o conteúdo final de
`extracted/GLOBAL_INDEX.md`. Não rode `extract.py` — este prompt é só para
quando os `_index.json` de cada espaço já existem e você só quer atualizar a
tabela global (por exemplo, depois de extrair um espaço novo manualmente).
