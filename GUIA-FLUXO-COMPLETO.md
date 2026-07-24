# Fluxo completo — do Confluence bruto à documentação organizada

Pressupõe que você já fez a configuração inicial (`LEIA-PRIMEIRO.md`, seções
3–4). Ordem recomendada, repetível a cada rodada de trabalho.

## Fase 1 — Extrair

1. Extraia primeiro os espaços de **leitura** (referência), um de cada vez:
   - Modo CLI: `python scripts/extract.py --space CHAVE`
   - Modo Chat: prompt `/extrair-espaco`
2. Extraia por último o espaço de **escrita** (o único onde você pode
   criar/editar) — mesmo comando/prompt.
3. Rode `python scripts/build_global_index.py` (ou prompt `/reindexar`) para
   atualizar `extracted/GLOBAL_INDEX.md`.

Resultado: `extracted/<CADA_ESPACO>/` com `_index.md`, `_index.json` e um
`content.md` + `meta.json` por página. Nenhum token de IA gasto até aqui.

Reextrair o mesmo espaço depois (fase 5, ou por rotina) é incremental por
padrão — só busca o que mudou. Para espaços muito grandes, veja
`LEIA-PRIMEIRO.md` (seção "Espaços grandes") para extrair em pedaços.

## Fase 2 — Pedir à IA para organizar

Com o conteúdo já local, use o Modo Chat (ou CLI) para pedir análise e
propostas — a IA nunca lê o Confluence diretamente, só os arquivos extraídos:

- "Veja `extracted/GLOBAL_INDEX.md` e me diga quais espaços têm páginas
  parecendo duplicadas ou desatualizadas."
- Prompt `/propor-organizacao` para um espaço, página ou grupo de páginas
  específico — gera arquivo(s) em `drafts/`, seguindo
  `templates/page-tone-guide.md`.

A IA nunca publica nada nesta fase — só escreve em `drafts/`.

## Fase 3 — Revisar

Leia o(s) arquivo(s) em `drafts/` como revisaria um texto de outra pessoa:
tom, precisão, se alguma informação do original ficou de fora (não deveria —
reorganizar e resumir com cuidado é permitido, remover não). Ajuste
diretamente o Markdown do rascunho se precisar.

## Fase 4 — Publicar

Só no espaço marcado `"mode": "write"` em `config/spaces.json`:

- Página nova → prompt `/criar-pagina` (ou `python scripts/publish.py create ...`).
- Página que a própria IA já criou antes → prompt `/editar-pagina-ia` (ou
  `python scripts/publish.py update ...`) — o script recusa sozinho se a
  página não estiver em `.ai-managed-pages.json`.

Confirme o comando final antes de rodar — publicar é sempre um passo
explícito.

## Fase 5 — Reextrair o espaço de escrita

Depois de publicar, rode `extract.py --space <ESPACO_DE_ESCRITA>` de novo
(ou `/extrair-espaco`) para que `extracted/` reflita o que está no Confluence
agora, incluindo a nova versão da página publicada. Isso mantém o índice e o
conteúdo local sempre coerentes com o que existe de verdade no Confluence.

## Repita

Nada aqui é "rodar uma vez só" — o fluxo normal é: extrair de novo sempre que
o conteúdo original mudar no Confluence, e usar as fases 2–5 sempre que
quiser organizar mais uma parte da documentação.
