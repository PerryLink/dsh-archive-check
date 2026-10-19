# dsh-archive-check — Comprobación de la integridad del registro de archivo y del plazo de conservación

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

```sh
dsh plugin --profile <name> add dsh-archive-check
```


[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-archive-check` lee un 归档登记表 (registro de archivo) —los asientos con las columnas que el propio registro trae, más el fondo y el año que cubre— y comprueba lo que un registro puede sostener mecánicamente: que cada asiento lleve los campos de descripción que usted configure, que el 档号 sea único dentro del registro, que el 件号 corra sin huecos, que el 保管期限 use un término de su propia tabla de plazos, que el 形成日期 se pueda analizar y coincida con el año del registro, y que se señalen los asientos que hayan superado el plazo de transferencia que usted configure.

## Cómo se ve la salida

![Terminal demo of dsh-archive-check: real output over its AR-002 fixture](https://raw.githubusercontent.com/PerryLink/dsh-archive-check/main/docs/assets/dsh-archive-check-hero.png)

![Animated terminal demo of dsh-archive-check](https://raw.githubusercontent.com/PerryLink/dsh-archive-check/main/docs/assets/dsh-archive-check-demo.gif)

Salida real de este plugin sobre su propio fixture de prueba `AR-002` — no es un montaje. El paquete de reglas no inventa citas, así que cada hallazgo nombra la cláusula aplicada y advierte que su texto no se obtuvo.

## Qué responde

| Usted pregunta | Qué responde |
|---|---|
| No he configurado ningún campo de descripción obligatorio. ¿La comprobación de la descripción pasa en silencio? | No. Mientras `requiredFields` esté vacío, `AR-001` se declara en `skipped`, de modo que una lista de diferencias vacía no se lee como «no falta nada». Cuando indique los nombres de sus columnas, solo comprueba que cada campo esté relleno en cada asiento —una cadena vacía cuenta como no relleno— y no juzga si la descripción es exacta. |
| Dos asientos llevan el mismo 档号, pero uno tiene un espacio en medio. ¿Sigue siendo duplicado? | Sí. `AR-002` compara el 档号 ignorando los espacios, así que 「A-2026-001」 y 「A-2026- 001」 cuentan como el mismo número. Está limitado a `warn` porque la cláusula que cita enuncia la unicidad como principio de elaboración, y no como una prohibición literal de repetir dentro de un mismo registro; un hallazgo suele significar un registro duplicado o un 档号 mal escrito, que aún debe confirmar una persona. |
| La columna 保管期限 dice algo que nuestra tabla de plazos no recoge. ¿Qué informa la comprobación? | `AR-003` separa dos casos: un valor que el analizador no reconoce como plazo (reconoce 「永久」「长期」「定期N年」「N年」) y un término reconocible que no está en la lista `retentionTerms` que usted configure. Las correcciones son distintas, por eso los mensajes son distintos. La regla nunca decide qué plazo merece un documento, y un plazo más largo que el marco nacional no es un error: las disposiciones que cita el paquete fijan las cifras de empresa como mínimo. |
| Los 件号 son 1, 2, 4 — ¿se informa del 3 que falta? | Sí, pero solo para 件号 escritos con dígitos puros: `AR-004` comprueba la continuidad únicamente en esos casos; un 件号 con letras o espacios queda fuera de la comparación y no informa de ninguna diferencia. Un hueco no es por sí mismo un defecto —puede que ese número no se haya usado—, así que el hallazgo solo pide confirmar si algún asiento quedó sin registrar. Con `checkSequence: false` la regla no se ejecuta. |
| El 形成日期 figura como 「二〇二六年三月十五日」. ¿Se lee? | No. `AR-005` lo informa como «no se puede analizar», que es un mensaje distinto del de una fecha cuyo año no coincide con el año del registro: apuntan a correcciones diferentes. Archivar entre años está permitido, y la regla no decide en qué año debería figurar un documento. |
| ¿Cómo sabe la comprobación que ya toca transferir? | `AR-007` compara el 形成日期 de cada asiento con el `transferAfterYears` que usted configure e informa solo de si ese plazo ya venció según los años fijados. El parámetro sale de fábrica como `0`, es decir, sin configurar, así que la regla se declara en `skipped` hasta que usted lo fije; con `requireFormedAt: true` también se informa por separado de los asientos sin 形成日期, porque no hay fecha desde la que calcular el vencimiento. La regla no juzga si la transferencia debería adelantarse o aplazarse. |

## Normas que sigue

| Documento | Número | Reglas que lo citan |
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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-rc.2`. **`engines.dsh` se declara como `>=0.2.1-0 <0.3.0`** y el host lo aplica desde 0.2.1 |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native` y `ptc`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-archive-check
dsh --profile <name> --dump-config | grep 'dsh-archive-check'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/archive-check.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-archive-check
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## Familia de plugins DSH de PerryLink

Este proyecto forma parte de la familia de plugins de DeepSeek Harness de [PerryLink](https://github.com/PerryLink). El registro permanece plegado abajo para que cada README conserve una primera pantalla corta; expándelo para ver cada fila y su estado.

<details>
<summary>Expandir todos los plugins</summary>

| Plugin | Estado |
|---|---|
| **[dsh-aqua-input-check](https://github.com/PerryLink/dsh-aqua-input-check)** |  |
| **[dsh-archive-check](https://github.com/PerryLink/dsh-archive-check)** |  |
| **[dsh-auto-review](https://github.com/PerryLink/dsh-auto-review)** |  |
| **[dsh-autotier](https://github.com/PerryLink/dsh-autotier)** |  |
| **[dsh-bid-ca-precheck](https://github.com/PerryLink/dsh-bid-ca-precheck)** |  |
| **[dsh-bid-qual-check](https://github.com/PerryLink/dsh-bid-qual-check)** |  |
| **[dsh-cert-mcp](https://github.com/PerryLink/dsh-cert-mcp)** |  |
| **[dsh-checkpoint-rewind](https://github.com/PerryLink/dsh-checkpoint-rewind)** |  |
| **[dsh-click](https://github.com/PerryLink/dsh-click)** |  |
| **[dsh-composer-history](https://github.com/PerryLink/dsh-composer-history)** |  |
| **[dsh-contract-stance](https://github.com/PerryLink/dsh-contract-stance)** |  |
| **[dsh-customs-doc-check](https://github.com/PerryLink/dsh-customs-doc-check)** |  |
| **[dsh-data-quality](https://github.com/PerryLink/dsh-data-quality)** |  |
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
| **[dsh-memento](https://github.com/PerryLink/dsh-memento)** |  |
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
| **[dsh-plugin-doctor](https://github.com/PerryLink/dsh-plugin-doctor)** |  |
| **[dsh-plugin-guide](https://github.com/PerryLink/dsh-plugin-guide)** |  |
| **[dsh-plugin-kit](https://github.com/PerryLink/dsh-plugin-kit)** |  |
| **[dsh-plugin-upgrade](https://github.com/PerryLink/dsh-plugin-upgrade)** |  |
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
| **[dsh-score](https://github.com/PerryLink/dsh-score)** |  |
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
| **[dsh-ticktick](https://github.com/PerryLink/dsh-ticktick)** |  |
| **[dsh-translate](https://github.com/PerryLink/dsh-translate)** |  |
| **[dsh-warranty-calc](https://github.com/PerryLink/dsh-warranty-calc)** |  |
| **[dsh-budget](https://github.com/PerryLink/dsh-budget)** | 🧊 CONGELADO — ver el README del repositorio |
| **[dsh-claude-move](https://github.com/PerryLink/dsh-claude-move)** | 🧊 CONGELADO — ver el README del repositorio |
| **[dsh-defend](https://github.com/PerryLink/dsh-defend)** | 🧊 CONGELADO — ver el README del repositorio |
| **[dsh-draw](https://github.com/PerryLink/dsh-draw)** | 🧊 CONGELADO — ver el README del repositorio |
| **[dsh-reach](https://github.com/PerryLink/dsh-reach)** | 🧊 CONGELADO — ver el README del repositorio |
| **[dsh-background-agents](https://github.com/PerryLink/dsh-background-agents)** | 🚫 RETIRADO — ver el README del repositorio |
| **[dsh-session-pin](https://github.com/PerryLink/dsh-session-pin)** | 🚫 RETIRADO — ver el README del repositorio |
| **[dsh-team-rooms](https://github.com/PerryLink/dsh-team-rooms)** | 🚫 RETIRADO — ver el README del repositorio |

</details>## License

[Apache License 2.0](LICENSE) © 2026 dsh-archive-check contributors.
