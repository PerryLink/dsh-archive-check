<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/dsh-archive-check-hero-en-dark.webp">
  <img src="docs/assets/dsh-archive-check-hero-en-light.webp" width="100%" alt="Banner do dsh-archive-check: à esquerda, o nome e o valor; à direita, ① o registo de arquivo (n.º de arquivo, título, prazo, n.º de item, data; o número repetido e o número de item em falta estão assinalados) → ② a lista das sete regras (AR-002/AR-004 diferença, AR-005/AR-006 sem diferença, AR-001/AR-003/AR-007 não configuradas) → ③ o cartão de ocorrência (AR-004, linha 3, falta o item 3) e a lista de não executadas; uma lista de diferenças vazia não significa «tudo bem» e a decisão fica com quem revê">
</picture>

# dsh-archive-check

**Verifica linha a linha um registo de arquivo: descrição completa, 档号 únicos, 件号 sem falhas, prazos de conservação conforme a sua própria tabela e datas legíveis — e devolve uma lista do que está inconsistente, onde e como corrigir.**

Um plugin de verificação de arquivos para DeepSeek Harness, feito para arquivistas e pessoal de escritório: o pacote de regras cita a regulamentação literalmente, assinala apenas diferenças literais face às cláusulas citadas, e nunca decide conformidade, nunca atribui responsabilidade e nunca toca no original.

[Instalar](#instalação-em-três-passos) · [Configuração](#configuração) · [FAQ](#faq) · [简体中文](README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [हिन्दी](README.hi.md)

[![License](https://img.shields.io/badge/license-Apache--2.0-3366CC?style=flat-square&labelColor=2B3245)](LICENSE)
[![DSH](https://img.shields.io/badge/DSH-%E2%89%A50.2.1%20%3C0.3.0-4B67B4?style=flat-square&labelColor=2B3245)](#compatibilidade)
[![npm](https://img.shields.io/npm/v/dsh-archive-check?style=flat-square&labelColor=2B3245&color=CB3837)](https://www.npmjs.com/package/dsh-archive-check)
[![CI](https://img.shields.io/github/actions/workflow/status/PerryLink/dsh-archive-check/ci.yml?branch=main&label=CI&style=flat-square&labelColor=2B3245)](https://github.com/PerryLink/dsh-archive-check/actions/workflows/ci.yml)
[![Node](https://img.shields.io/badge/node-%5E22.19%20%7C%7C%20%3E%3D24-339933?style=flat-square&labelColor=2B3245)](#compatibilidade)

[![Stars](https://img.shields.io/github/stars/PerryLink/dsh-archive-check?style=flat-square&labelColor=2B3245)](https://github.com/PerryLink/dsh-archive-check/stargazers)
[![npm downloads](https://img.shields.io/npm/dm/dsh-archive-check?style=flat-square&labelColor=2B3245&color=CB3837)](https://www.npmjs.com/package/dsh-archive-check)
[![dshfind](https://dshfind.com/api/badge/PerryLink/dsh-archive-check?metric=downloads)](https://dshfind.com/plugins/PerryLink/dsh-archive-check?ref=badge)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/PerryLink/dsh-archive-check/badge)](https://securityscorecards.dev/viewer/?uri=github.com/PerryLink/dsh-archive-check)
[![DSH Market](https://img.shields.io/badge/DSH_Market-listed-4B67B4?style=flat-square&labelColor=2B3245)](https://dsh.market/)
[![Gitee](https://img.shields.io/badge/Gitee-mirror-C71D23?style=flat-square&labelColor=2B3245&logo=gitee)](https://gitee.com/perrylink/dsh-archive-check)

```sh
dsh plugin --profile <name> add dsh-archive-check
```

</div>

<sub>Plugin da comunidade, sem afiliação com a DeepSeek. Repositório canónico: <https://github.com/PerryLink/dsh-archive-check> (o Gitee é um espelho).</sub>

## O que é

`dsh-archive-check` lê um 归档登记表 (registo de arquivo) — os itens com as colunas que o próprio registo traz, mais o fundo e o ano que abrange — e verifica o que um registo pode sustentar mecanicamente: se cada item traz os campos de descrição que você configurar, se o 档号 é único dentro do registo, se o 件号 corre sem falhas, se o 保管期限 usa um termo da sua própria tabela de prazos, se o 形成日期 é analisável e coincide com o ano do registo, e se são assinalados os itens que passaram do prazo de transferência que você configurar. Você entrega o material original (uma tabela, um registo ou um documento; Excel pode ser convertido antes para JSON/YAML, até no chat se a plataforma permitir) e recebe uma lista de «que linha, que coluna, o que falta». Não decide conformidade, não atribui responsabilidade, não substitui o revisor — e jamais modifica o original.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/dsh-archive-check-flow-v5-dark.svg">
  <img src="docs/assets/dsh-archive-check-flow-v5-light.svg" width="100%" alt="Estrutura do dsh-archive-check: as sete regras à esquerda, cada uma com o campo que lê, a cláusula que cita e o tipo de fundamento; os cinco documentos e as suas onze cláusulas literais à direita; as linhas contínuas são a base principal e as tracejadas a base adicional; o tipo de fundamento limita a gravidade; uma execução mostra AR-002/AR-004 com diferença, AR-005/AR-006 sem diferença e AR-001/AR-003/AR-007 não configuradas; cada diferença leva linha, coluna e cláusula, e cada verificação não executada indica o motivo">
</picture>

## Instalação em três passos

1. **Instale**:

   ```sh
   dsh plugin --profile <name> add dsh-archive-check
   ```

   Em alternativa, procure «Professional Document Check Suite» no WorkBuddy / Coze (o conjunto completo; esta verificação é uma parte; disponibilidade conforme a loja).

2. **Configuração mínima** (funciona com os valores padrão):

   ```yaml
   - insert:
       - id: dsh-archive-check
         name: dsh-archive-check
   ```

   Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts` e os padrões estão prontos a usar; os limites por regra ficam no pacote de regras sob `rules/`.

3. **Verifique que monta**:

   ```sh
   dsh --profile <name> --dump-config | grep 'dsh-archive-check'
   ```

   Depois execute o exemplo incluído (cerca de um minuto):

   ```sh
   node samples/quickstart/run.mjs --check
   ```

   A entrada de exemplo está em `samples/quickstart/input/`, a saída esperada em `samples/quickstart/expected/result.json` e uma captura da execução em `docs/assets/quickstart.png`.

**Desinstalar**: `dsh plugin --profile <name> remove dsh-archive-check` (ou remova a linha do patch do perfil).

<details>
<summary>Instalar a partir do mercado do DSH Desktop</summary>

Todos os plugins da PerryLink podem ser explorados no mercado integrado do DSH Desktop: **Market → Sources → Add source → colar** `https://perrylink-dsh-catalog.perrylink.workers.dev/catalog-source.json` **→ selecionar**. A instalação continua a exigir a verificação de identidade npm do mercado e a sua confirmação.

</details>

## Capacidades principais

O plugin regista a ferramenta `archive_check`: lê um registo (os itens com as suas colunas, mais o fundo e o ano), aplica um pacote de regras versionado e devolve um relatório estruturado.

- **O pacote de regras é dado, não código** — todas as regras vivem em `rules/archive-check.yaml`; trocar o ficheiro troca o conjunto de regras sem tocar em TypeScript, e o pacote é validado ao carregar, não é confiado.
- **A severidade segue a evidência** — uma regra baseada num princípio geral (`derived-from-principle`) tem teto `warn`; uma baseada na configuração da sua instituição (`institutional-configuration`) tem teto `info`; nenhuma pode ser declarada `error` (um teste garante-o).
- **Uma lista vazia nunca é «tudo em ordem»** — cada verificação que não pôde executar-se declara-se em `skipped` com o seu motivo, e uma regra cuja lista obrigatória não está configurada declara-se em `skipped` em vez de passar em silêncio.
- **Sem adjudicação** — o relatório apenas enumera diferenças e nunca se pronuncia sobre conformidade, responsabilidade ou correção; um guarda de redação obriga a que o relatório traga sempre o aviso.
- **Citações só literais** — cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e o URL de onde foi lido; um trecho com menos de oito caracteres, ou um que não pôde ser obtido, diz isso no próprio trecho e marca a regra como `derived-from-principle` — uma paráfrase nunca é apresentada como citação.

```text
registo (fundo · ano · itens) ──archive_check──▶ regras AR-001…AR-007 ──▶ relatório (findings + skipped)
            ▲                                                                                 │
            └─────────────────────────── o original nunca é modificado ───────────────────────┘
```

### Regras em resumo

| Regra | Verificação | Severidade | Tipo de base |
|---|---|---|---|
| `AR-001` | cada item traz os teus campos de descrição obrigatórios (desligada por padrão) | info | local |
| `AR-002` | o 档号 é único dentro do registo | warn | princípio |
| `AR-003` | o 保管期限 usa um termo da tua tabela (desligada por padrão) | info | local |
| `AR-004` | os 件号 são únicos e sem falhas dentro do registo | warn | princípio |
| `AR-005` | o 形成日期 é analisável e o seu ano coincide com o do registo | warn | princípio |
| `AR-006` | o registo declara o seu fundo e o seu ano | warn | princípio |
| `AR-007` | itens que ultrapassam o teu prazo de transferência configurado (desligada por padrão) | info | local |

### Exemplos

São os pontos de entrada reais do plugin; instala uma vez e chama um.

**Saída detalhada** — ferramenta `archive_check`, entrada:

```json
{"fonds":"某单位","year":2026,"items":[{"档号":"A-2026-001","题名":"","保管期限":"永久", ...}]}
```

Saída:

```json
{
  "id": "dsh-archive-check.AR-001.de09b5a6",
  "ruleId": "AR-001",
  "severity": "info",
  "locator": {
    "row": 1
  },
  "found": "第 1 行缺少 题名",
  "expected": "按本机构配置，归档条目应著录 档号、题名、保管期限",
  "fix": "补齐著录项目；本条只核对字段是否存在，不判断著录内容是否准确"
}
```

*Observado em `dsh-archive-check/tests/fixtures/AR-001/AR-001-unsafe.json; dsh-archive-check/tests/fixtures/AR-001/cases.json; dsh-archive-check/rules/archive-check.yaml; dsh-archive-check/tests/index.test.ts`*

### O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| Não configurei nenhum campo de descrição obrigatório. A verificação da descrição passa em silêncio? | Não. Enquanto `requiredFields` estiver vazio, o `AR-001` declara-se em `skipped`, de modo que uma lista de diferenças vazia não é lida como «não falta nada». Depois de indicar os nomes das suas colunas, verifica apenas que cada campo está preenchido em cada item —uma cadeia vazia conta como não preenchido— e não julga se a descrição está correta. |
| Dois itens trazem o mesmo 档号, mas um tem um espaço no meio. Continua a ser duplicado? | Sim. O `AR-002` compara o 档号 ignorando os espaços, por isso 「A-2026-001」 e 「A-2026- 001」 contam como o mesmo número. Está limitado a `warn` porque a cláusula que cita enuncia a unicidade como princípio de elaboração, e não como proibição literal de repetir dentro do mesmo registo; um achado costuma significar registo duplicado ou 档号 mal escrito, que ainda tem de ser confirmado por uma pessoa. |
| A coluna 保管期限 diz algo que a nossa tabela de prazos não prevê. O que é que a verificação reporta? | O `AR-003` separa dois casos: um valor que o analisador não reconhece como prazo (reconhece 「永久」「长期」「定期N年」「N年」) e um termo reconhecível que não está na lista `retentionTerms` que você configurar. As correções são diferentes, por isso as mensagens são diferentes. A regra nunca decide que prazo um documento merece, e um prazo mais longo do que o quadro nacional não é erro: as disposições citadas pelo pacote fixam as cifras para as empresas como mínimo. |
| Os 件号 são 1, 2, 4 — o 3 em falta é reportado? | Sim, mas só para 件号 escritos com dígitos puros: o `AR-004` verifica a continuidade apenas nesses casos; um 件号 com letras ou espaços fica fora da comparação e não reporta diferença alguma. Uma falha não é por si só um defeito —pode o número não ter sido usado—, por isso o achado apenas pede que se confirme se algum item ficou por registar. Com `checkSequence: false` a regra não é executada. |
| O 形成日期 está escrito como 「二〇二六年三月十五日」. É lido? | Não. O `AR-005` reporta-o como «não é possível analisar», que é uma mensagem diferente da de uma data cujo ano não coincide com o ano do registo: apontam para correções diferentes. Arquivar entre anos é permitido, e a regra não decide em que ano um documento deveria ficar. |
| Como é que a verificação sabe que a transferência está a vencer? | O `AR-007` compara o 形成日期 de cada item com o `transferAfterYears` que você configurar e reporta apenas se esse prazo já passou segundo os anos fixados. O parâmetro vem de fábrica como `0`, ou seja, por configurar, por isso a regra declara-se em `skipped` até você o definir; com `requireFormedAt: true`, os itens sem 形成日期 são também reportados em separado, porque não há data a partir da qual calcular o vencimento. A regra não julga se a transferência deveria ser antecipada ou adiada. |

## Configuração

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`. As cinco chaves da tabela são a lista completa; os parâmetros por regra vêm a seguir.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/archive-check.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

Parâmetros por regra que vale a pena conhecer:

- `AR-001` `requiredFields` — as colunas que cada linha tem de preencher, p. ex. `[档号, 题名, 保管期限, 责任者]`. Vazio significa que a regra não é executada. Uma célula em branco conta como não preenchida.
- `AR-003` `retentionTerms` — os termos que a sua tabela de prazos usa, p. ex. `[永久, 定期30年, 定期10年]`; também pode ser passado por chamada para uma comparação pontual.
- `AR-004` `checkSequence` — ponha `false` para deixar de verificar a continuidade dos 件号.
- `AR-006` `requireHeader` — ponha `false` se o seu registo legitimamente não traz fundo nem ano.
- `AR-007` `transferAfterYears` — o prazo de transferência do **seu** arquivo: `20` para um arquivo recetor central / provincial / sub-provincial, `10` para um de nível de condado (segundo o regulamento de execução citado). `0` significa que a regra não é executada. `AR-007` `requireFormedAt` torna uma coluna 形成日期 em falta um achado em vez de uma omissão, porque sem data não se calcula o vencimento.

## FAQ

<details>
<summary>O meu material é modificado ou enviado para algum lado?</summary>

Não. A ferramenta apenas lê o texto JSON/YAML que você entrega e **nunca modifica o original**; o plugin é ESM puro, sem código nativo, **sem rede e sem chamada ao modelo** (ver Compatibilidade), por isso o material nunca sai da sua máquina.

</details>

<details>
<summary>Sem campos obrigatórios nem tabela configurados, algo passa em silêncio?</summary>

Não. As duas listas — `requiredFields` do `AR-001` e `retentionTerms` do `AR-003` — vêm de fábrica vazias, e uma regra cuja lista não está configurada declara-se em `skipped` com o motivo, por isso uma lista de diferenças vazia nunca é lida como «não falta nada». O `AR-003` também pode ser alimentado por chamada para uma comparação pontual sem editar o pacote de regras.

</details>

<details>
<summary>O plugin instala mas a ferramenta nunca aparece — e agora?</summary>

Confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou; um `main` errado faz o carregador saltar a entrada em silêncio.

</details>

<details>
<summary>A instalação é recusada por versão incompatível — e agora?</summary>

A faixa de peers cobre as linhas `0.1.x` e `0.2.x`; se o seu runtime ficar fora dela, conceda uma isenção explícita: `dsh plugin --profile <name> allow-version dsh-archive-check@0.1.0 --dsh-version <runtime> --accept-risk`. A compatibilidade de peers é aplicada pelo runtime ao instalar.

</details>

<details>
<summary>Aguenta um ano inteiro de registos ou um diretório completo em lote?</summary>

A ferramenta funciona nos modos `native` e `ptc`; para um ano de registos use `ptc`, assim o custo do esquema paga-se uma só vez. Toda a aritmética é de hora local sobre as cadeias entregues, sem conversão de fusos horários.

</details>

## Normas que segue

| Documento | Número | Regras que o citam |
|---|---|---|
| 《归档文件整理规则》 | DA/T 22—2015 | AR-001, AR-002, AR-004, AR-005, AR-006 |
| 《中华人民共和国档案法实施条例》 | 国务院令第772号 | AR-001, AR-003, AR-007 |
| 《机关文件材料归档范围和文书档案保管期限规定》 | 国家档案局令第8号 | AR-003 |
| 《企业文件材料归档范围和档案保管期限规定》 | 国家档案局令第10号 | AR-003 |
| 《中华人民共和国档案法》 | 2020年修订（主席令第四十七号） | AR-007 |

**Limite:** este plugin verifica um **归档登记表** (registo de arquivo) naquilo que um registo pode sustentar mecanicamente: se cada item está descrito com completude suficiente para ser arquivado e recuperado, se o 档号 é único, se o 件号 corre sem falhas, se os prazos vêm da sua tabela e se o 形成日期 é analisável e coincide com o ano do registo. **Não** decide se um documento concreto deveria ter sido arquivado, nem que prazo merece. Essas são decisões do arquivista.

> ### ⚠️ Três coisas que este plugin se recusa a fazer, e porquê
>
> **1. Nunca decide que prazo de conservação um documento merece.** Não existe **uma tabela nacional
> única de prazos** que se possa aplicar. O regulamento de execução (artigo 19.º, segundo parágrafo)
> e a Portaria n.º 8 (artigo 12.º) exigem que cada instituição compile o seu próprio âmbito de
> arquivo e a sua própria tabela de prazos e a submeta à aprovação da autoridade arquivística; e a
> Portaria n.º 10 (artigo 11.º) diz que as cifras para empresas são um **mínimo** — uma empresa pode
> legalmente escolher um prazo *mais longo*. Por isso o `AR-003` só verifica que a redação é uma das
> que você configurou, e um teste garante que o pacote diz que um prazo mais longo «não é um erro».
>
> **2. Coloca os anos de transferência onde pertencem.** As cifras de 20 / 10 anos estão no
> regulamento de execução (artigo 20.º, segundo parágrafo), ligadas ao *nível do arquivo recetor*,
> e não a se a unidade é uma empresa. O artigo 15.º da Lei dos Arquivos **não contém cifra alguma** —
> diz apenas «de acordo com as disposições estatais pertinentes, periodicamente». Atribuir «20 anos»
> ao artigo 15.º seria fabricação, e um teste garante que o pacote não o faz.
>
> **3. Não usa o primeiro artigo já obsoleto.** O artigo 1.º da Portaria n.º 8 cita as medidas de
> execução de 1999, que o regulamento de 2024 (Decreto do Conselho de Estado n.º 772) revogou no seu
> artigo 52.º. O pacote nunca o cita, e um teste garante-o.
>
> Há duas listas que são suas, não da lei: os campos de descrição obrigatórios (`AR-001`) e o seu
> vocabulário de prazos (`AR-003`). Ambas vêm de fábrica **vazias**, e uma regra cuja lista não está
> configurada declara-se em `skipped` em vez de passar em silêncio.

## Formato do material

A ferramenta aceita JSON ou YAML:

```yaml
fonds: 某单位
year: 2026
items:
  - { 档号: A-2026-001, 题名: 关于第一项工作的通知, 保管期限: 永久,   形成日期: 2026-03-15, 件号: "1" }
  - { 档号: A-2026-002, 题名: 关于第二项工作的通知, 保管期限: 定期30年, 形成日期: 2026-04-01, 件号: "2" }
```

Os nomes de coluna são reconhecidos entre `档号`/`档案号`, `题名`/`文件题名`/`标题`, `保管期限`/`期限`, `形成日期`/`成文日期`/`日期` e `件号`/`序号`. Uma simples lista de títulos também serve: cada cadeia torna-se o 题名 de um item. Os números são aceites como cadeias, por isso uma exportação de folha de cálculo não precisa de limpeza.

O 保管期限 é lido em duas formas: `永久`/`长期` para permanente, e qualquer `N年`/`定期N年`/`N` simples para prazo fixo. Um termo ilegível é reportado como ilegível, o que é diferente de um termo fora da sua lista configurada: produzem achados diferentes, porque precisam de correções diferentes.

## Fontes das regras

Os dados das regras vivem em `rules/archive-check.yaml`, separados do código. Cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e o URL de onde foi lido. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas num princípio geral ou numa política local **nunca** seja declarada `error`.

As cláusulas citadas vêm de:

- **《中华人民共和国档案法》** (revisão de 2020-06-20, 主席令第四十七号, em vigor desde 2021-01-01) — artigos 13.º–15.º, 21.º, 37.º, 39.º
- **《中华人民共和国档案法实施条例》** (**国务院令第772号**, publicada em 2024-01-12, **em vigor desde 2024-03-01**; o seu artigo 52.º revoga as medidas de execução de 1999) — artigos 19.º, 20.º, 24.º, 39.º, 40.º
- **《机关文件材料归档范围和文书档案保管期限规定》** (国家档案局令第8号) — artigos 3.º, 4.º, 6.º, 12.º, 14.º
- **《企业文件材料归档范围和档案保管期限规定》** (国家档案局令第10号) — artigos 7.º, 11.º, 15.º, 16.º
- **《归档文件整理规则》** (DA/T 22—2015) — 5.2.2, 5.3.1, 5.4.1, 5.4.3 e), 5.5.2

Três correções deram forma a este pacote e ficam registadas no seu cabeçalho:

1. **O regulamento foi substituído.** O Decreto do Conselho de Estado n.º 772 está em vigor desde 2024-03-01 e revoga as medidas de 1999, por isso o artigo 1.º da Portaria n.º 8 (que cita o texto revogado) nunca é citado.
2. **Os anos de transferência estão no regulamento, não na lei.** O artigo 20.º, segundo parágrafo, traz as cifras de 20/10 anos e liga-as ao nível do arquivo recetor; o artigo 15.º da Lei dos Arquivos não tem cifra alguma.
3. **Não existe uma tabela de prazos universal.** Cada instituição compila a sua e submete-a a aprovação, e as cifras das empresas são um mínimo legal, não um teto.

O relatório completo de verificação de cláusulas, incluindo as fontes revistas e rejeitadas, está em `rules/evidence/clause-verification.md`.

## Compatibilidade

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-rc.2`. `engines.dsh` é declarado como `>=0.2.1-0 <0.3.0` e o host o aplica desde 0.2.1 |
| Node | `^22.19.0 \|\| >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native` e `ptc`; para um ano de registos use `ptc` |

## Resolução de problemas

- **`AR-001` e `AR-003` declaram-se em `skipped`.** As suas listas estão vazias. O `AR-003` também pode ser alimentado por chamada, por isso uma comparação pontual não precisa de editar o pacote de regras.
- **`AR-004` não reporta nada.** Menos de dois 件号 foram analisados como inteiros puros: as referências alfanuméricas ficam deliberadamente fora da verificação de continuidade, em vez de serem adivinhadas.
- **`AR-005` dispara sobre uma data que eu consigo ler.** O leitor aceita `2026-03-15` e `2026-03-15 09:30`; uma data em numerais chineses é reportada como não analisável de propósito, para que decida se normaliza a exportação.
- **O leitor recusa um registo que antes aceitava.** Não encontrou nenhuma das colunas de arquivo conhecidas; o erro nomeia as colunas que viu.
- **O plugin instala mas a ferramenta nunca aparece.** Confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou; um `main` errado faz o carregador saltar a entrada em silêncio.
- **`dsh plugin add` recusa o pacote como incompatível.** A faixa de peers cobre `0.1.x` e `0.2.x`; se o seu runtime ficar fora, conceda isenção explícita: `dsh plugin --profile <name> allow-version dsh-archive-check@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` informa `manifest-peers` como falha.** O verificador estático compara contra uma faixa de peers fixada em código anterior à linha 0.2. O runtime aplica a compatibilidade ao instalar, por isso a faixa declarada é a correta; é um problema conhecido do `dsh-plugin-dev`.
- **Os horários parecem deslocados.** Toda a aritmética é de hora local sobre as cadeias fornecidas, sem conversão de fusos horários.

## Ecossistema e qualidade

- [Espelho do Gitee](https://gitee.com/perrylink/dsh-archive-check) (espelho sincronizado; o GitHub é canónico)
- [Página do plugin no dshfind](https://dshfind.com/plugins/PerryLink/dsh-archive-check) (instalações e ranking)
- [Relatório do OpenSSF Scorecard](https://securityscorecards.dev/viewer/?uri=github.com/PerryLink/dsh-archive-check) (impulsionado por [.github/workflows/scorecard.yml](.github/workflows/scorecard.yml))
- [DSH Market](https://dsh.market/) (listado)
- [Base de conhecimento do ecossistema — escolha um verificador por material](https://perrylink.github.io/zh/checkers/choose/) (índice completo da família: 62 verificadores + plugins gerais)

## Desenvolvimento

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, fixtures emparelhados por regra (tests/fixtures/<RULE>/)
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
pnpm run check:readmes   # consistência dos README em cinco idiomas
node ../scripts/sync-shared.mjs dsh-archive-check   # refresca src/shared a partir de ../_shared
```

O pacote de regras é dado, não código: edite `rules/*.yaml` para trocar o conjunto de regras sem tocar em TypeScript; o pacote é validado ao carregar, não é confiado. As imagens do README são geradas programaticamente por [`scripts/gen-readme-assets.py`](scripts/gen-readme-assets.py) (Pillow para o hero localizado e um SVG escrito à mão para a figura de estrutura) e podem ser reexecutadas sem risco; este plugin não tem UI e a figura de estrutura usa apenas tokens da superfície de comandos, identificadores de regras/campos/cláusulas e breves legendas em inglês.

Topics: `dsh`, `dsh-plugin`, `deepseek-harness`, `cordis`, `archive`

## Família e agradecimentos

Este projeto faz parte da família de plugins DeepSeek Harness mantida por [PerryLink](https://github.com/PerryLink) (todos Apache-2.0). Se lhe for útil, **uma estrela** não desbloqueia nada, mas ajuda a próxima pessoa a encontrá-lo.

- [@PerryLink](https://github.com/PerryLink) — criador e mantenedor: a ferramenta `archive_check`, o pacote de regras com citações literais e o seu registo de verificação de cláusulas, e a documentação em cinco idiomas.

<details>
<summary>Expandir todos os plugins</summary>

| Plugin | Estado |
|---|---|
| **[dsh-aqua-input-check](https://github.com/PerryLink/dsh-aqua-input-check)** |  |
| **[dsh-archive-check](https://github.com/PerryLink/dsh-archive-check)** |  |
| **[dsh-auto-review](https://github.com/PerryLink/dsh-auto-review)** |  |
| **[dsh-autotier](https://github.com/PerryLink/dsh-autotier)** | 🧊 CONGELADO — ver o README do repo |
| **[dsh-bid-ca-precheck](https://github.com/PerryLink/dsh-bid-ca-precheck)** |  |
| **[dsh-bid-qual-check](https://github.com/PerryLink/dsh-bid-qual-check)** |  |
| **[dsh-cert-mcp](https://github.com/PerryLink/dsh-cert-mcp)** | 🧊 CONGELADO — ver o README do repo |
| **[dsh-checkpoint-rewind](https://github.com/PerryLink/dsh-checkpoint-rewind)** |  |
| **[dsh-click](https://github.com/PerryLink/dsh-click)** |  |
| **[dsh-composer-history](https://github.com/PerryLink/dsh-composer-history)** |  |
| **[dsh-contract-stance](https://github.com/PerryLink/dsh-contract-stance)** |  |
| **[dsh-customs-doc-check](https://github.com/PerryLink/dsh-customs-doc-check)** |  |
| **[dsh-data-quality](https://github.com/PerryLink/dsh-data-quality)** | 🧊 CONGELADO — ver o README do repo |
| **[dsh-demurrage-ledger](https://github.com/PerryLink/dsh-demurrage-ledger)** |  |
| **[dsh-doublecheck](https://github.com/PerryLink/dsh-doublecheck)** |  |
| **[dsh-drill-script-check](https://github.com/PerryLink/dsh-drill-script-check)** |  |
| **[dsh-eia-guide-check](https://github.com/PerryLink/dsh-eia-guide-check)** |  |
| **[dsh-emergency-plan](https://github.com/PerryLink/dsh-emergency-plan)** |  |
| **[dsh-essay-rubric-check](https://github.com/PerryLink/dsh-essay-rubric-check)** |  |
| **[dsh-evidence-check](https://github.com/PerryLink/dsh-evidence-check)** |  |
| **[dsh-export-ctl-check](https://github.com/PerryLink/dsh-export-ctl-check)** |  |
| **[dsh-fast](https://github.com/PerryLink/dsh-fast)** |  |
| **[dsh-fmea-table-check](https://github.com/PerryLink/dsh-fmea-table-check)** |  |
| **[dsh-forecast-penalty](https://github.com/PerryLink/dsh-forecast-penalty)** |  |
| **[dsh-fund-research](https://github.com/PerryLink/dsh-fund-research)** |  |
| **[dsh-github](https://github.com/PerryLink/dsh-github)** |  |
| **[dsh-gongwen-flow-check](https://github.com/PerryLink/dsh-gongwen-flow-check)** |  |
| **[dsh-gongwen-word-check](https://github.com/PerryLink/dsh-gongwen-word-check)** |  |
| **[dsh-guard-plan-qc](https://github.com/PerryLink/dsh-guard-plan-qc)** |  |
| **[dsh-hazchem-check](https://github.com/PerryLink/dsh-hazchem-check)** |  |
| **[dsh-hazplan-check](https://github.com/PerryLink/dsh-hazplan-check)** |  |
| **[dsh-hidden-risk-map](https://github.com/PerryLink/dsh-hidden-risk-map)** |  |
| **[dsh-hs-classify](https://github.com/PerryLink/dsh-hs-classify)** |  |
| **[dsh-icd-rule-check](https://github.com/PerryLink/dsh-icd-rule-check)** |  |
| **[dsh-industry-research](https://github.com/PerryLink/dsh-industry-research)** |  |
| **[dsh-lawcite-adapter](https://github.com/PerryLink/dsh-lawcite-adapter)** |  |
| **[dsh-laya](https://github.com/PerryLink/dsh-laya)** |  |
| **[dsh-lc-doc-check](https://github.com/PerryLink/dsh-lc-doc-check)** |  |
| **[dsh-learning-gap-check](https://github.com/PerryLink/dsh-learning-gap-check)** |  |
| **[dsh-library](https://github.com/PerryLink/dsh-library)** |  |
| **[dsh-local-ai](https://github.com/PerryLink/dsh-local-ai)** |  |
| **[dsh-lsp-actions](https://github.com/PerryLink/dsh-lsp-actions)** |  |
| **[dsh-mask](https://github.com/PerryLink/dsh-mask)** |  |
| **[dsh-mcp-panel](https://github.com/PerryLink/dsh-mcp-panel)** |  |
| **[dsh-medrec-qc](https://github.com/PerryLink/dsh-medrec-qc)** |  |
| **[dsh-memento](https://github.com/PerryLink/dsh-memento)** | 🧊 CONGELADO — ver o README do repo |
| **[dsh-nsfc-form-check](https://github.com/PerryLink/dsh-nsfc-form-check)** |  |
| **[dsh-nurse-record-check](https://github.com/PerryLink/dsh-nurse-record-check)** |  |
| **[dsh-observe](https://github.com/PerryLink/dsh-observe)** |  |
| **[dsh-origin-rvc-check](https://github.com/PerryLink/dsh-origin-rvc-check)** |  |
| **[dsh-ota-review-check](https://github.com/PerryLink/dsh-ota-review-check)** |  |
| **[dsh-output-styles](https://github.com/PerryLink/dsh-output-styles)** |  |
| **[dsh-paper-doc-adapter](https://github.com/PerryLink/dsh-paper-doc-adapter)** |  |
| **[dsh-permission-rules](https://github.com/PerryLink/dsh-permission-rules)** |  |
| **[dsh-permit-report-check](https://github.com/PerryLink/dsh-permit-report-check)** |  |
| **[dsh-pipeline-check](https://github.com/PerryLink/dsh-pipeline-check)** |  |
| **[dsh-pleading-draft](https://github.com/PerryLink/dsh-pleading-draft)** |  |
| **[dsh-plugin-doctor](https://github.com/PerryLink/dsh-plugin-doctor)** | 🚫 APOSENTADO (repo arquivado) |
| **[dsh-plugin-guide](https://github.com/PerryLink/dsh-plugin-guide)** |  |
| **[dsh-plugin-kit](https://github.com/PerryLink/dsh-plugin-kit)** | 🚫 APOSENTADO (repo arquivado) |
| **[dsh-plugin-upgrade](https://github.com/PerryLink/dsh-plugin-upgrade)** | 🚫 APOSENTADO (repo arquivado) |
| **[dsh-policy-brief-draft](https://github.com/PerryLink/dsh-policy-brief-draft)** |  |
| **[dsh-power-loss-split](https://github.com/PerryLink/dsh-power-loss-split)** |  |
| **[dsh-power-ticket-check](https://github.com/PerryLink/dsh-power-ticket-check)** |  |
| **[dsh-ppap-check](https://github.com/PerryLink/dsh-ppap-check)** |  |
| **[dsh-protest-deadline](https://github.com/PerryLink/dsh-protest-deadline)** |  |
| **[dsh-railway-window](https://github.com/PerryLink/dsh-railway-window)** |  |
| **[dsh-repair-order-qc](https://github.com/PerryLink/dsh-repair-order-qc)** |  |
| **[dsh-research-report](https://github.com/PerryLink/dsh-research-report)** |  |
| **[dsh-review-reply-check](https://github.com/PerryLink/dsh-review-reply-check)** |  |
| **[dsh-rulefile-check](https://github.com/PerryLink/dsh-rulefile-check)** |  |
| **[dsh-safety-brief-check](https://github.com/PerryLink/dsh-safety-brief-check)** |  |
| **[dsh-score](https://github.com/PerryLink/dsh-score)** | 🧊 CONGELADO — ver o README do repo |
| **[dsh-session-sync](https://github.com/PerryLink/dsh-session-sync)** |  |
| **[dsh-site-log-check](https://github.com/PerryLink/dsh-site-log-check)** |  |
| **[dsh-skill-pack-security](https://github.com/PerryLink/dsh-skill-pack-security)** |  |
| **[dsh-soe-decision-check](https://github.com/PerryLink/dsh-soe-decision-check)** |  |
| **[dsh-soilwater-check](https://github.com/PerryLink/dsh-soilwater-check)** |  |
| **[dsh-sop-sync-check](https://github.com/PerryLink/dsh-sop-sync-check)** |  |
| **[dsh-spc-gbt-adapter](https://github.com/PerryLink/dsh-spc-gbt-adapter)** |  |
| **[dsh-talk](https://github.com/PerryLink/dsh-talk)** |  |
| **[dsh-tender-extract](https://github.com/PerryLink/dsh-tender-extract)** |  |
| **[dsh-tender-matrix](https://github.com/PerryLink/dsh-tender-matrix)** |  |
| **[dsh-test-drive](https://github.com/PerryLink/dsh-test-drive)** |  |
| **[dsh-ticktick](https://github.com/PerryLink/dsh-ticktick)** | 🚫 APOSENTADO (repo arquivado) |
| **[dsh-translate](https://github.com/PerryLink/dsh-translate)** |  |
| **[dsh-warranty-calc](https://github.com/PerryLink/dsh-warranty-calc)** |  |
| **[dsh-budget](https://github.com/PerryLink/dsh-budget)** | 🧊 CONGELADO — ver o README do repo |
| **[dsh-claude-move](https://github.com/PerryLink/dsh-claude-move)** | 🧊 CONGELADO — ver o README do repo |
| **[dsh-defend](https://github.com/PerryLink/dsh-defend)** | 🧊 CONGELADO — ver o README do repo |
| **[dsh-draw](https://github.com/PerryLink/dsh-draw)** | 🧊 CONGELADO — ver o README do repo |
| **[dsh-reach](https://github.com/PerryLink/dsh-reach)** | 🧊 CONGELADO — ver o README do repo |
| **[dsh-background-agents](https://github.com/PerryLink/dsh-background-agents)** | 🚫 APOSENTADO (repo arquivado) |
| **[dsh-session-pin](https://github.com/PerryLink/dsh-session-pin)** | 🚫 APOSENTADO (repo arquivado) |
| **[dsh-team-rooms](https://github.com/PerryLink/dsh-team-rooms)** | 🚫 APOSENTADO (repo arquivado) |

</details>

## Licença

[LICENSE](LICENSE) (Apache License 2.0) © 2026 dsh-archive-check contributors

<p align="center"><sub>Apache-2.0 · Plugin da comunidade, sem afiliação com a DeepSeek.</sub></p>
