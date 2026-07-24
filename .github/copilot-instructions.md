# Instruções do projeto — Documentação Confluence

Este repositório contém conteúdo extraído de espaços do Confluence (pasta
`extracted/`, um subdiretório por espaço) e, quando aplicável, rascunhos de
páginas novas ou reorganizadas em `drafts/`, antes de serem publicadas de
volta no espaço editável.

## O que fazer em cada situação

- **Extrair ou reextrair um espaço do Confluence** → prompt `extrair-espaco`.
- **Só atualizar o índice global (sem chamar a API)** → prompt `reindexar`.
- **Propor reorganização, resumo ou melhoria de um espaço/página** → prompt
  `propor-organizacao`. Isso só gera um rascunho em `drafts/` — não publica
  nada sozinho.
- **Criar uma página nova no espaço editável** → prompt `criar-pagina`.
- **Editar uma página que a própria IA criou** → prompt `editar-pagina-ia`.
- Para qualquer uma dessas ações no modo Chat, o agente `confluence-documentador`
  já traz as regras abaixo embutidas — selecione-o no dropdown do chat.

## Regras obrigatórias deste repositório

- **Nunca proponha excluir conteúdo do Confluence.** O script `publish.py`
  nem tem comando de exclusão — isso é intencional.
- **Só é permitido editar (`publish.py update`) páginas que já estejam em
  `.ai-managed-pages.json`** — ou seja, páginas criadas por este toolkit.
  Página que já existia antes no Confluence é só leitura para a IA, mesmo que
  pareça desatualizada; se precisar mudar, é o usuário quem edita direto no
  Confluence.
- **`publish.py create` só funciona no espaço marcado `"mode": "write"`** em
  `config/spaces.json` — o script recusa qualquer outro espaço.
- **Antes de propor reorganização de um espaço**, confira se
  `extracted/<ESPACO>/_index.md` existe e é recente; se não existir, rode o
  prompt `extrair-espaco` primeiro.
- **Siga sempre `templates/page-tone-guide.md`** ao escrever ou reescrever
  texto de página — não repita essas regras de tom a cada conversa, apenas
  aplique o arquivo.
- **Nunca sugira versionar `config/.env`** (contém ou referencia credenciais).
- **Confirme com o usuário antes de rodar `publish.py create` ou `update`** —
  mesmo com as travas de código acima, publicar no Confluence real deve ser
  um passo explícito, nunca automático.
- Links internos entre páginas só são resolvidos automaticamente dentro do
  mesmo espaço e na mesma rodada de extração — ao propor uma página nova,
  confira manualmente se algum link cruza espaços antes de publicar.

## Referências rápidas

- `LEIA-PRIMEIRO.md` — visão geral, os dois modos de uso (CLI e Chat), onde
  colocar o repositório no Windows.
- `GUIA-FLUXO-COMPLETO.md` — ordem recomendada do fluxo completo.
- `MENU-ATIVIDADES-PONTUAIS.md` — atalhos para tarefas do dia a dia.
- `templates/page-tone-guide.md` — regras de tom de escrita.
