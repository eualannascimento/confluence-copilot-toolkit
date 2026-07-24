---
mode: confluence-documentador
description: Propõe uma reorganização, resumo ou melhoria de documentação para um espaço ou página já extraída, sem publicar nada.
---
Espaço: ${input:espaco:space key já extraído}
Escopo: ${input:escopo:ex. "página X", "todo o espaço", "as páginas sobre Y"}
Objetivo: ${input:objetivo:ex. "unificar páginas duplicadas", "deixar o tom consistente", "criar uma página de visão geral"}

1. Confira se `extracted/${input:espaco}/_index.md` existe e está atualizado;
   se não, rode o prompt `extrair-espaco` antes de continuar.
2. Leia o índice do espaço e só os `content.md` relevantes ao escopo pedido
   — não abra o espaço inteiro se o escopo for menor.
3. Escreva a proposta em `drafts/` (um arquivo por página proposta ou
   reescrita), seguindo `templates/page-tone-guide.md`.
4. Ao final, apresente um resumo do que mudou em relação ao conteúdo
   original e liste explicitamente qualquer informação que você resumiu ou
   reorganizou (nunca removeu) para o usuário conferir antes de publicar.
5. Não chame `scripts/publish.py` neste prompt — publicação é um passo
   separado (prompts `criar-pagina` / `editar-pagina-ia`), sempre confirmado
   pelo usuário.
