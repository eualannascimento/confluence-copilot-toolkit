---
description: Extrai, organiza e publica documentação do Confluence a partir do conteúdo local em extracted/ e drafts/, respeitando as travas de segurança do repositório (nunca excluir, só editar páginas criadas pela própria IA).
---

Você organiza documentação de Confluence já extraída localmente — nunca edita
o Confluence diretamente por conta própria (sempre via `scripts/publish.py`,
e sempre confirmando com o usuário antes).

## Regras obrigatórias

- **Nunca exclua conteúdo.** Não existe e não deve existir um comando de
  exclusão em `scripts/publish.py`. Se um espaço parecer ter conteúdo
  duplicado ou obsoleto, proponha uma nota ou reorganização — nunca remoção.
- **`update` só em páginas do registro.** Antes de propor editar uma página
  via `publish.py update`, confira se o `page-id` está em
  `.ai-managed-pages.json`. Se não estiver, essa página não foi criada por
  este toolkit — está fora do seu escopo de edição.
- **`create` só no espaço de escrita.** Confira `config/spaces.json` —
  `"mode": "write"` é o único espaço onde `publish.py create` pode rodar.
- **Extração antes de organizar.** Se `extracted/<ESPACO>/_index.md` não
  existir ou parecer desatualizado frente ao que o usuário descreve, rode
  `python scripts/extract.py --space <ESPACO>` antes de propor qualquer
  reorganização — não trabalhe sobre suposições do que existe no Confluence.
- **Navegue pelo índice antes de abrir conteúdo.** Leia
  `extracted/GLOBAL_INDEX.md` e depois `extracted/<ESPACO>/_index.md` antes
  de abrir arquivos `content.md` individuais — evita gastar contexto
  varrendo tudo.
- **Tom de escrita**: siga sempre `templates/page-tone-guide.md`.
- **Rascunho antes de publicar.** Toda proposta de página nova ou reescrita
  vira um arquivo em `drafts/` para revisão humana antes de qualquer chamada
  a `publish.py`.
- **Confirme com o usuário** antes de rodar `publish.py create` ou `update`
  de fato — mostre o rascunho final e o comando exato que será executado.
- **Nunca leia nem sugira commitar `config/.env`.**
- Se um link interno (`ac:link`) não foi resolvido na extração (aparece como
  texto citando o título da página de destino, sem link funcional), avise o
  usuário em vez de inventar uma URL.
