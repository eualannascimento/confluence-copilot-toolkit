# Confluence + Copilot — Como usar este kit

Este kit resolve duas pontas do mesmo problema:

1. **Extrair** o máximo de conteúdo do Confluence on-premise da sua empresa
   para arquivos Markdown locais, com índice, sem gastar tokens de IA nesse
   processo (script Python puro) e sem baixar anexos (só links diretos).
2. **Usar uma IA** (VS Code + GitHub Copilot) sobre esse conteúdo extraído
   para organizar, resumir e padronizar a documentação — e, quando aprovado,
   publicar de volta apenas no seu espaço editável, nunca excluindo nada e só
   editando páginas que a própria IA criou.

Este kit **não reimplementa** nada de terceiros (não existe um pacote de
skills pronto para Confluence como existe para Power BI) — os scripts em
`scripts/` e os arquivos em `.github/` são deste kit mesmo.

## Dois jeitos de rodar — e por que existem os dois

| | **Modo CLI** (GitHub Copilot CLI) | **Modo Chat** (extensão GitHub Copilot Chat no VS Code) |
|---|---|---|
| O que é | `copilot`, rodado no terminal (inclusive o terminal integrado do VS Code) | O painel de chat do VS Code, modo *Agent* |
| Como aciona as regras deste kit | Lê `.github/copilot-instructions.md` automaticamente | Você seleciona o agente `confluence-documentador` no dropdown do chat, ou digita um `/prompt-file` |
| Como aciona um passo específico | Descreva o que quer, ou digite `/extrair-espaco`, `/criar-pagina` etc. | Mesmos prompt files, mesma sintaxe `/nome-do-arquivo` |
| Melhor para | Fluxos de terminal, rodar os scripts Python diretamente | Revisão de conteúdo, edição de rascunhos, quem prefere não abrir terminal separado |

Os arquivos em `.github/prompts/*.prompt.md` funcionam **nos dois modos** —
digitando `/extrair-espaco`, `/propor-organizacao`, `/criar-pagina`,
`/editar-pagina-ia` ou `/reindexar`. O agente `.github/agents/confluence-documentador.agent.md`
só aparece no dropdown do **Modo Chat** (no Modo CLI, as mesmas regras já
vêm de `copilot-instructions.md`).

Você não precisa escolher um só: use o Modo CLI para rodar `extract.py`/`publish.py`
direto, e o Modo Chat para revisar e ajustar o conteúdo com calma.

---

## 1. Pré-requisitos

- **Python 3.10+** instalado no Windows (verifique com `python --version` no
  terminal do VS Code).
- **VS Code** com a extensão **GitHub Copilot Chat** (Modo Chat) e/ou o
  **GitHub Copilot CLI** (`npm install -g @github/copilot`, Modo CLI).
- Acesso ao Confluence on-premise da empresa com usuário/senha válidos (ou
  Personal Access Token, se sua instância permitir — veja `config/.env.example`).

## 2. Onde colocar este repositório no Windows

Recomendado: uma pasta dentro de `Documentos` do seu usuário Windows, por
exemplo:

```
C:\Users\<seu-usuario>\Documents\confluence-docs\
```

Um único repositório para todos os espaços (ao contrário de "um repo por
projeto") — o índice global (`extracted/GLOBAL_INDEX.md`) e a navegação
cruzada entre espaços só funcionam bem centralizados num só lugar. Cada
espaço fica isolado em `extracted/<SPACE_KEY>/`, então o `git diff`/histórico
por espaço continua limpo mesmo estando tudo no mesmo repositório.

Abra o VS Code **na raiz** deste repositório (`confluence-docs/`), não dentro
de `extracted/` ou `scripts/` — assim `.github/copilot-instructions.md`, o
agente e os prompt files valem para tudo.

## 3. Copiar o kit para o repositório real

Este kit foi montado como um **modelo/starter kit** — não é, em si, o seu
repositório de trabalho. Copie o conteúdo para dentro da pasta real
(`confluence-docs/`, seção 2 acima):

```bash
cp -r confluence-copilot-toolkit/.github     confluence-docs/
cp -r confluence-copilot-toolkit/scripts     confluence-docs/
cp -r confluence-copilot-toolkit/templates   confluence-docs/
cp    confluence-copilot-toolkit/.gitignore  confluence-docs/
cp -r confluence-copilot-toolkit/config      confluence-docs/
```

No Windows, o equivalente em PowerShell:

```powershell
Copy-Item -Recurse confluence-copilot-toolkit\.github     confluence-docs\
Copy-Item -Recurse confluence-copilot-toolkit\scripts     confluence-docs\
Copy-Item -Recurse confluence-copilot-toolkit\templates   confluence-docs\
Copy-Item          confluence-copilot-toolkit\.gitignore  confluence-docs\
Copy-Item -Recurse confluence-copilot-toolkit\config      confluence-docs\
```

## 4. Configurar

Dentro de `confluence-docs/`:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r scripts\requirements.txt
```

Depois:

1. Copie `config/.env.example` para `config/.env` e preencha
   `CONFLUENCE_BASE_URL` e `CONFLUENCE_AUTH_MODE` (veja os comentários no
   próprio arquivo — provavelmente `basic`, já que a licença on-premise
   expira sem PAT confirmado).
2. Copie `config/spaces.example.json` para `config/spaces.json` e liste suas
   *space keys* reais, marcando `"mode": "write"` só no espaço onde você pode
   criar/editar páginas — todos os outros ficam `"mode": "read"`.

Nenhum dos dois arquivos deve ser commitado (já estão no `.gitignore`).

## 5. Primeiro teste

Comece por um espaço pequeno de **leitura**, não pelo espaço de escrita:

```powershell
python scripts\extract.py --space SEUESPACOTESTE
python scripts\build_global_index.py
```

Confira `extracted/SEUESPACOTESTE/_index.md` e uma ou duas páginas em
`extracted/SEUESPACOTESTE/<pagina>/content.md` antes de rodar para os demais
espaços. Só depois disso valer a pena, siga para
`GUIA-FLUXO-COMPLETO.md`.

## Os outros documentos deste kit

- **`GUIA-FLUXO-COMPLETO.md`** — ordem recomendada do fluxo completo:
  configurar → extrair → gerar índice → pedir à IA para organizar → revisar
  → publicar.
- **`MENU-ATIVIDADES-PONTUAIS.md`** — atalhos para tarefas pontuais do dia a
  dia, nos dois modos.
- **`templates/page-tone-guide.md`** — o tom de escrita que toda página
  proposta pela IA deve seguir.

## Espaços grandes: extraia em pedaços, incremental por padrão

Rodar `extract.py` num espaço com centenas de páginas pode demorar ou
esbarrar em limites do servidor on-premise. O script já ajuda com isso:

- **Reextrair o mesmo espaço é incremental por padrão** — só busca páginas
  alteradas desde a extração anterior (lida do `_index.json` já existente).
  As páginas não alteradas continuam intactas, sem reprocessar. Use `--full`
  para forçar uma extração completa mesmo já havendo uma anterior.
- **Baixar só um pedaço do espaço**, em vez do espaço inteiro de uma vez:
  - `--parent-id 123456` — só a subárvore a partir dessa página.
  - `--label alguma-label` — só páginas com essa label.
  - `--since 2026-07-01` — só páginas alteradas depois dessa data.
  - `--page-size 20` — lotes menores por requisição (útil se o servidor for
    lento ou instável).
- **Interrupção não perde o trabalho feito.** Se a extração cair no meio
  (Ctrl+C, VPN caindo, timeout), os índices são regravados com o que já foi
  concluído antes de sair, e rodar o mesmo comando de novo completa o
  restante — o script sai com código 130 nesse caso, para você saber que foi
  parcial.

## Limitações conhecidas (leia antes de confiar 100% na extração)

- A conversão de macros do Confluence para Markdown cobre os casos mais
  comuns (código, avisos/notas, imagens, anexos, links internos, tabelas).
  Macros incomuns viram uma nota visível (`_[macro Confluence não convertida
  automaticamente: ...]_`) em vez de desaparecer — se aparecer, confira a
  página original no Confluence para esse trecho.
- Links internos (`ac:link`) só são resolvidos automaticamente entre páginas
  do **mesmo espaço** extraídas na **mesma rodada**. Links entre espaços
  diferentes viram texto citando o título da página de destino, sem link
  clicável — é esperado, não é bug.
- Anexos nunca são baixados — sempre um link direto de download (se a API
  expôs um) ou uma nota apontando a página onde o anexo está.
