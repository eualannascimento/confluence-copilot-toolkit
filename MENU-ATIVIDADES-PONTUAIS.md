# Menu de atividades pontuais

Atalhos para tarefas do dia a dia, nos dois modos. Veja `GUIA-FLUXO-COMPLETO.md`
para o fluxo completo ordenado.

| Quero... | Modo CLI / terminal | Modo Chat |
|---|---|---|
| Reextrair um espaço específico (incremental, só o que mudou) | `python scripts/extract.py --space CHAVE` | `/extrair-espaco` |
| Extrair um espaço inteiro do zero (ignora o incremental) | `python scripts/extract.py --space CHAVE --full` | pedir em linguagem natural |
| Extrair só uma subárvore (espaço grande demais de uma vez) | `python scripts/extract.py --space CHAVE --parent-id ID` | pedir em linguagem natural |
| Continuar uma extração que caiu no meio | rodar o mesmo comando de novo (é incremental por padrão) | idem |
| Só atualizar o índice global | `python scripts/build_global_index.py` | `/reindexar` |
| Resumir uma página | pedir em linguagem natural, apontando o `content.md` | idem, no chat |
| Propor reorganização de 1 página ou de um espaço inteiro | pedir em linguagem natural | `/propor-organizacao` |
| Criar página nova no espaço editável | `python scripts/publish.py create --space CHAVE --title "..." --file drafts/arquivo.md` | `/criar-pagina` |
| Editar página que a IA criou | `python scripts/publish.py update --page-id ID --file drafts/arquivo.md` | `/editar-pagina-ia` |
| Ver o que a IA tem permissão de editar | abrir `.ai-managed-pages.json` | idem |
| Conferir se um espaço está marcado leitura ou escrita | abrir `config/spaces.json` | idem |

## Perguntas rápidas que a IA já sabe responder olhando os arquivos locais

- "Quais espaços já foram extraídos e quando?" → `extracted/GLOBAL_INDEX.md`
- "Essa página tem anexos?" → `meta.json` da página (`attachment_count`,
  lista de `attachments` com URL de download)
- "Essa página faz parte de qual hierarquia?" → campo `ancestors` no
  `meta.json` ou a indentação em `_index.md`
- "Alguma página deste espaço tem link interno não resolvido?" → procurar por
  `_(página do Confluence:` nos arquivos `content.md` do espaço
