# Tom de escrita para páginas do Confluence

Toda página nova ou reorganizada por este toolkit segue o mesmo tom, para o
conjunto da documentação parecer escrito por uma única pessoa:

## Que tipo de página é esta? (Diátaxis)

Antes de escrever ou reorganizar, classifique a página numa destas quatro
categorias — é o padrão usado por documentações como Kubernetes, GitLab e
Django, porque cada categoria responde a uma necessidade diferente do leitor
e mistura mal com as outras:

| Categoria | Responde a | Sinal de que está errada |
|---|---|---|
| **Tutorial** | "Me guie do zero até um resultado" | Tem decisões/alternativas no meio — tutorial não escolhe, só executa |
| **Guia prático (how-to)** | "Como eu faço [tarefa específica]?" | Explica conceito em vez de ir direto ao passo a passo |
| **Referência** | "Qual o valor/parâmetro/campo exato de X?" | Tem prosa longa em vez de ser consultável rapidamente |
| **Explicação** | "Por que isso funciona assim?" | Tem passo a passo — isso pertence ao how-to, não aqui |

Se uma página existente mistura duas categorias (comum em documentação
antiga — ex.: um "como configurar X" que no meio explica a arquitetura
inteira), isso é candidato a virar duas páginas, não uma reescrita no lugar.
Proponha a divisão explicitamente ao usuário em vez de decidir sozinho.

- **Direto**: vai ao ponto na primeira frase de cada seção; sem rodeios nem
  introduções genéricas ("Neste documento vamos falar sobre...").
- **Discreto**: sem adjetivos de autopromoção, sem exagero. Descreve o que é
  e como usar, não o quão importante ou inovador é.
- **Elegante**: frases curtas, bem pontuadas, sem gírias nem informalidade.
- **Orientativo**: sempre que fizer sentido, termina indicando o próximo
  passo ou onde encontrar mais detalhe (link para outra página já extraída,
  quando existir).
- **Sucinto**: prefere listas e parágrafos curtos a blocos longos de texto.
  Corta qualquer frase que não mude o entendimento do leitor.
- **Explicativo**: assume que quem lê pode não conhecer o contexto — define
  siglas e termos técnicos na primeira aparição da página.
- **Formal**: português correto, sem abreviações de chat, sem emoji.

## Checklist antes de propor ou publicar uma página

- [ ] O título descreve o conteúdo sem precisar abrir a página para entender.
- [ ] O primeiro parágrafo resume do que se trata, sem precisar de contexto externo.
- [ ] Termos técnicos e siglas têm uma explicação na primeira ocorrência.
- [ ] Não há informação removida em relação ao conteúdo original — apenas
      reorganizada, resumida com cuidado ou clarificada.
- [ ] Links internos apontam para páginas reais (checar `_index.md` do espaço).
- [ ] Nenhum anexo foi "perdido" — cada um aparece como link ou nota de
      referência à página original.
