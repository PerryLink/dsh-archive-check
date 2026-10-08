# dsh-archive-check — Verificação da integridade do registo de arquivo e do prazo de conservação

`dsh-archive-check` lê um 归档登记表 (registo de arquivo) —os itens com as colunas que o próprio registo traz, mais o fundo e o ano que abrange— e verifica o que um registo pode sustentar mecanicamente: se cada item traz os campos de descrição que você configurar, se o 档号 é único dentro do registo, se o 件号 corre sem falhas, se o 保管期限 usa um termo da sua própria tabela de prazos, se o 形成日期 é analisável e coincide com o ano do registo, e se são assinalados os itens que passaram do prazo de transferência que você configurar.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| Não configurei nenhum campo de descrição obrigatório. A verificação da descrição passa em silêncio? | Não. Enquanto `requiredFields` estiver vazio, o `AR-001` declara-se em `skipped`, de modo que uma lista de diferenças vazia não é lida como «não falta nada». Depois de indicar os nomes das suas colunas, verifica apenas que cada campo está preenchido em cada item —uma cadeia vazia conta como não preenchido— e não julga se a descrição está correta. |
| Dois itens trazem o mesmo 档号, mas um tem um espaço no meio. Continua a ser duplicado? | Sim. O `AR-002` compara o 档号 ignorando os espaços, por isso 「A-2026-001」 e 「A-2026- 001」 contam como o mesmo número. Está limitado a `warn` porque a cláusula que cita enuncia a unicidade como princípio de elaboração, e não como proibição literal de repetir dentro do mesmo registo; um achado costuma significar registo duplicado ou 档号 mal escrito, que ainda tem de ser confirmado por uma pessoa. |
| A coluna 保管期限 diz algo que a nossa tabela de prazos não prevê. O que é que a verificação reporta? | O `AR-003` separa dois casos: um valor que o analisador não reconhece como prazo (reconhece 「永久」「长期」「定期N年」「N年」) e um termo reconhecível que não está na lista `retentionTerms` que você configurar. As correções são diferentes, por isso as mensagens são diferentes. A regra nunca decide que prazo um documento merece, e um prazo mais longo do que o quadro nacional não é erro: as disposições citadas pelo pacote fixam as cifras para as empresas como mínimo. |
| Os 件号 são 1, 2, 4 — o 3 em falta é reportado? | Sim, mas só para 件号 escritos com dígitos puros: o `AR-004` verifica a continuidade apenas nesses casos; um 件号 com letras ou espaços fica fora da comparação e não reporta diferença alguma. Uma falha não é por si só um defeito —pode o número não ter sido usado—, por isso o achado apenas pede que se confirme se algum item ficou por registar. Com `checkSequence: false` a regra não é executada. |
| O 形成日期 está escrito como 「二〇二六年三月十五日」. É lido? | Não. O `AR-005` reporta-o como «não é possível analisar», que é uma mensagem diferente da de uma data cujo ano não coincide com o ano do registo: apontam para correções diferentes. Arquivar entre anos é permitido, e a regra não decide em que ano um documento deveria ficar. |
| Como é que a verificação sabe que a transferência está a vencer? | O `AR-007` compara o 形成日期 de cada item com o `transferAfterYears` que você configurar e reporta apenas se esse prazo já passou segundo os anos fixados. O parâmetro vem de fábrica como `0`, ou seja, por configurar, por isso a regra declara-se em `skipped` até você o definir; com `requireFormedAt: true`, os itens sem 形成日期 são também reportados em separado, porque não há data a partir da qual calcular o vencimento. A regra não julga se a transferência deveria ser antecipada ou adiada. |

## Normas que segue

| Documento | Número | Regras que o citam |
|---|---|---|
| 《归档文件整理规则》 | DA/T 22—2015 | AR-001, AR-002, AR-004, AR-005, AR-006 |
| 《中华人民共和国档案法实施条例》 | 国务院令第772号 | AR-001, AR-003, AR-007 |
| 《机关文件材料归档范围和文书档案保管期限规定》 | 国家档案局令第8号 | AR-003 |
| 《企业文件材料归档范围和档案保管期限规定》 | 国家档案局令第10号 | AR-003 |
| 《中华人民共和国档案法》 | 2020年修订（主席令第四十七号） | AR-007 |

**Boundary:** this plugin checks one **归档登记表** (filing register) for the things a register can be
held to mechanically — that each item is described completely enough to be filed and found again, that
档号 is unique, that 件号 runs without gaps, that retention terms come from your schedule, and that
形成日期 parses and matches the register's year. It does **not** decide whether a particular document
belonged in the archive, nor which retention period it deserves. Those are the archivist's judgements.

> ### ⚠️ Three things this plugin refuses to do, and why
>
> **1. It never decides which retention period a document deserves.** There is **no single national
> retention table** you can apply. 《档案法实施条例》第十九条第二款 and 国家档案局令第8号第十二条 require each
> institution to compile its own 归档范围 and 保管期限表 and have it approved by the档案 authority; and
> 国家档案局令第10号第十一条 says the enterprise figures are a **minimum** — an enterprise may lawfully
> choose a *longer* period. So `AR-003` checks only that the wording is one you have configured, and a
> test asserts that the pack says a longer period "is not an error".
>
> **2. It puts the transfer years where they belong.** The 20-year / 10-year figures are in
> **《档案法实施条例》第二十条第二款**, keyed to the *receiving archive's level*, not to whether the unit
> is an enterprise. 《档案法》第十五条 contains **no year figure at all** — it says only "按照国家有关规定，
> 定期". Attributing "满20年" to the law's article 15 would be fabrication, and a test asserts the pack
> does not.
>
> **3. It does not use the outdated first article.** 国家档案局令第8号's 第一条 cites the 1999
> 《档案法实施办法》, which the 2024 条例 (国务院令第772号) repealed in its 第五十二条. The pack never cites it,
> and a test asserts that.
>
> Two lists are yours, not the law's: the required description fields (`AR-001`) and your retention
> vocabulary (`AR-003`). Both ship **empty**, and a rule whose list is unset reports itself in `skipped`
> rather than passing silently.

## Compatibility

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-archive-check
dsh --profile <name> --dump-config | grep 'dsh-archive-check'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/archive-check.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-archive-check
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-archive-check contributors.
