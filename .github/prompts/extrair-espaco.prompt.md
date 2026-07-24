---
mode: confluence-documentador
description: Extrai (ou reextrai) um espaço do Confluence para Markdown local e atualiza os índices.
---
Espaço: ${input:espaco:space key do Confluence, ex. PROJX}

1. Rode no terminal: `python scripts/extract.py --space ${input:espaco}`.
   Isso já é incremental por padrão (só busca o que mudou desde a última
   extração). Se o espaço for muito grande e isso travar ou demorar demais,
   ofereça ao usuário extrair em pedaços: `--parent-id ID` (uma subárvore),
   `--label NOME` (só páginas com essa label), ou `--page-size 20` (lotes
   menores por requisição). Se a extração for interrompida no meio, rodar o
   mesmo comando de novo completa o restante — não é preciso recomeçar.
2. Depois, rode `python scripts/build_global_index.py` para atualizar o
   índice global.
3. Ao final, resuma: quantas páginas foram extraídas, quantas têm anexos, e
   se algum link interno ficou sem resolver (aparece como texto simples em
   vez de link em algum `content.md`) — se sim, avise quais páginas.
4. Não abra todo o conteúdo extraído — leia só `extracted/${input:espaco}/_index.md`
   para conferir o resultado.
