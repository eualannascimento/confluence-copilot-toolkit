---
mode: confluence-documentador
description: Propõe uma reorganização, resumo ou melhoria de documentação para um espaço ou página já extraída, sem publicar nada.
---
Espaço: ${input:espaco:space key já extraído}
Escopo: ${input:escopo:ex. "página X", "todo o espaço", "as páginas sobre Y"}
Objetivo: ${input:objetivo:ex. "unificar páginas duplicadas", "deixar o tom consistente", "criar uma página de visão geral"}

Siga estas fases — nunca pule direto para reescrever sem passar pelas duas primeiras:

## Fase 1 — Descoberta

Confira se `extracted/${input:espaco}/_index.md` existe e está atualizado; se
não, rode o prompt `extrair-espaco` antes de continuar. Leia o índice do
espaço e identifique todas as páginas dentro do escopo pedido — inclusive as
que só parecem relacionadas de longe (títulos parecidos, mesma hierarquia de
ancestrais). Não abra o espaço inteiro se o escopo for menor.

## Fase 2 — Análise de valor

Para cada página dentro do escopo, antes de propor qualquer mudança:
classifique-a segundo `templates/page-tone-guide.md` (tutorial / guia
prático / referência / explicação) e mapeie, seção por seção, o que é
conteúdo único (não existe em nenhuma outra página do escopo) versus
redundante (já coberto em outra página, ou desatualizado frente a uma
versão mais recente em outra página). Nunca decida remover uma seção só por
parecer redundante à primeira vista — se houver dúvida, mantenha e sinalize
para o usuário decidir.

## Fase 3 — Proposta

Escreva a proposta em `drafts/` (um arquivo por página proposta ou
reescrita), seguindo `templates/page-tone-guide.md`. Se uma página mistura
categorias Diátaxis diferentes (ex. tutorial com explicação de arquitetura no
meio), proponha a divisão em páginas separadas em vez de só reescrever no
lugar — explique essa divisão ao usuário, não decida silenciosamente.

## Fase 4 — Prestação de contas

Apresente um resumo do que mudou em relação ao conteúdo original: liste
explicitamente cada trecho que foi resumido, movido ou reorganizado (nunca
removido) para o usuário conferir antes de publicar, e liste separadamente
qualquer conteúdo que ficou marcado como "possivelmente redundante, mantido
por segurança" para o usuário decidir se descarta.

Não chame `scripts/publish.py` neste prompt — publicação é um passo separado
(prompts `criar-pagina` / `editar-pagina-ia`), sempre confirmado pelo usuário.
