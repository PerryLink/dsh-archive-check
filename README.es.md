<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/dsh-archive-check-hero-en-dark.webp">
  <img src="docs/assets/dsh-archive-check-hero-en-light.webp" width="100%" alt="Banner de dsh-archive-check: a la izquierda, el nombre y el valor; a la derecha, ① el registro de archivo (n.º de archivo, título, plazo, n.º de pieza, fecha; se marcan el número repetido y el número de pieza ausente) → ② la lista de siete reglas (AR-002/AR-004 diferencia, AR-005/AR-006 sin diferencia, AR-001/AR-003/AR-007 sin configurar) → ③ la tarjeta de hallazgo (AR-004, fila 3, falta la pieza 3) y la lista de no ejecutadas; una lista de diferencias vacía no significa que todo esté bien y el veredicto queda en manos de la persona revisora">
</picture>

# dsh-archive-check

**Comprueba fila a fila un registro de archivo: descripción completa, 档号 únicos, 件号 sin huecos, plazos de conservación según tu propia tabla y fechas legibles — y devuelve una lista de qué es inconsistente, dónde y cómo corregirlo.**

Un plugin de comprobación de archivos para DeepSeek Harness, hecho para archiveros y personal de oficina: el paquete de reglas cita la normativa literalmente, solo señala diferencias literales frente a las cláusulas citadas, y nunca decide conformidad, nunca atribuye responsabilidad y nunca toca el original.

[Instalar](#instalación-en-tres-pasos) · [Configuración](#configuración) · [FAQ](#faq) · [简体中文](README.md) · [English](README.en.md) · [Español](README.es.md) · [Português](README.pt.md) · [हिन्दी](README.hi.md)

[![License](https://img.shields.io/badge/license-Apache--2.0-3366CC?style=flat-square&labelColor=2B3245)](LICENSE)
[![DSH](https://img.shields.io/badge/DSH-%E2%89%A50.2.1%20%3C0.3.0-4B67B4?style=flat-square&labelColor=2B3245)](#compatibilidad)
[![npm](https://img.shields.io/npm/v/dsh-archive-check?style=flat-square&labelColor=2B3245&color=CB3837)](https://www.npmjs.com/package/dsh-archive-check)
[![CI](https://img.shields.io/github/actions/workflow/status/PerryLink/dsh-archive-check/ci.yml?branch=main&label=CI&style=flat-square&labelColor=2B3245)](https://github.com/PerryLink/dsh-archive-check/actions/workflows/ci.yml)
[![Node](https://img.shields.io/badge/node-%5E22.19%20%7C%7C%20%3E%3D24-339933?style=flat-square&labelColor=2B3245)](#compatibilidad)

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

<sub>Plugin de la comunidad, no afiliado a DeepSeek. Repositorio canónico: <https://github.com/PerryLink/dsh-archive-check> (Gitee es un espejo).</sub>

## Qué es

`dsh-archive-check` lee un 归档登记表 (registro de archivo) —los asientos con las columnas que el propio registro trae, más el fondo y el año que cubre— y comprueba lo que un registro puede sostener mecánicamente: que cada asiento lleve los campos de descripción que usted configure, que el 档号 sea único dentro del registro, que el 件号 corra sin huecos, que el 保管期限 use un término de su propia tabla de plazos, que el 形成日期 se pueda analizar y coincida con el año del registro, y que se señalen los asientos que hayan superado el plazo de transferencia que usted configure. Usted entrega el material original (una tabla, un registro o un documento; Excel puede convertirse antes a JSON/YAML, incluso en el chat si la plataforma lo permite) y recibe una lista de «qué fila, qué columna, qué falta». No decide conformidad, no atribuye responsabilidad, no sustituye al revisor —y jamás modifica el original.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/dsh-archive-check-flow-v5-dark.svg">
  <img src="docs/assets/dsh-archive-check-flow-v5-light.svg" width="100%" alt="Estructura de dsh-archive-check: las siete reglas a la izquierda, cada una con el campo que lee, la cláusula que cita y el tipo de fundamento; los cinco documentos y sus once cláusulas literales a la derecha; las líneas continuas son la base principal y las discontinuas la base adicional; el tipo de fundamento limita la gravedad; una ejecución muestra AR-002/AR-004 con diferencia, AR-005/AR-006 sin diferencia y AR-001/AR-003/AR-007 sin configurar; cada diferencia lleva fila, columna y cláusula, y cada comprobación no ejecutada indica el motivo">
</picture>

## Instalación en tres pasos

1. **Instala**:

   ```sh
   dsh plugin --profile <name> add dsh-archive-check
   ```

   También puedes buscar «Professional Document Check Suite» en WorkBuddy / Coze (el conjunto completo; esta comprobación es una parte; disponibilidad según la tienda).

2. **Configuración mínima** (funciona con los valores por defecto):

   ```yaml
   - insert:
       - id: dsh-archive-check
         name: dsh-archive-check
   ```

   Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts` y los valores por defecto están listos para usar; los umbrales por regla están en el paquete de reglas bajo `rules/`.

3. **Verifica que se monta**:

   ```sh
   dsh --profile <name> --dump-config | grep 'dsh-archive-check'
   ```

   Después ejecuta el ejemplo incluido (aproximadamente un minuto):

   ```sh
   node samples/quickstart/run.mjs --check
   ```

   La entrada de ejemplo está en `samples/quickstart/input/`, la salida esperada en `samples/quickstart/expected/result.json` y una captura de la ejecución en `docs/assets/quickstart.png`.

**Desinstalar**: `dsh plugin --profile <name> remove dsh-archive-check` (o elimina la fila del patch del perfil).

<details>
<summary>Instalar desde el mercado de DSH Desktop</summary>

Todos los plugins de PerryLink pueden explorarse en el mercado integrado de DSH Desktop: **Market → Sources → add source → pegar** `https://perrylink-dsh-catalog.perrylink.workers.dev/catalog-source.json` **→ seleccionarlo**. La instalación sigue pasando por la verificación de identidad npm del mercado y tu confirmación.

</details>

## Capacidades clave

El plugin registra la herramienta `archive_check`: lee un registro (los asientos con sus columnas, más el fondo y el año), aplica un paquete de reglas versionado y devuelve un informe estructurado.

- **El paquete de reglas es dato, no código** — todas las reglas viven en `rules/archive-check.yaml`; cambiar el archivo cambia el conjunto de reglas sin tocar TypeScript, y el paquete se valida al cargar, no se confía en él.
- **La severidad sigue a la evidencia** — una regla basada en un principio general (`derived-from-principle`) tiene tope `warn`; una basada en la configuración de tu institución (`institutional-configuration`) tiene tope `info`; ninguna puede declararse `error` (un test lo garantiza).
- **Una lista vacía nunca es «todo en orden»** — cada comprobación que no pudo ejecutarse se declara en `skipped` con su motivo, y una regla cuya lista obligatoria no está configurada se declara en `skipped` en lugar de pasar en silencio.
- **Sin adjudicación** — el informe solo enumera diferencias y nunca se pronuncia sobre conformidad, responsabilidad o corrección; un guardián de redacción obliga a que el informe lleve siempre el descargo.
- **Citas solo literales** — cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y la URL de donde se leyó; un extracto de menos de ocho caracteres, o uno que no pudo obtenerse, lo dice en el propio extracto y marca la regla como `derived-from-principle` — una paráfrasis nunca se presenta como cita.

```text
registro (fondo · año · asientos) ──archive_check──▶ reglas AR-001…AR-007 ──▶ informe (findings + skipped)
              ▲                                                                               │
              └────────────────────────── el original nunca se modifica ──────────────────────┘
```

### Reglas en resumen

| Regla | Comprobación | Severidad | Tipo de base |
|---|---|---|---|
| `AR-001` | cada asiento lleva tus campos de descripción obligatorios (apagada por defecto) | info | local |
| `AR-002` | el 档号 es único dentro del registro | warn | principio |
| `AR-003` | el 保管期限 usa un término de tu tabla (apagada por defecto) | info | local |
| `AR-004` | los 件号 son únicos y sin huecos dentro del registro | warn | principio |
| `AR-005` | el 形成日期 se puede analizar y su año coincide con el del registro | warn | principio |
| `AR-006` | el registro declara su fondo y su año | warn | principio |
| `AR-007` | asientos que superan tu plazo de transferencia configurado (apagada por defecto) | info | local |

### Ejemplos

Son los puntos de entrada reales del plugin; instala una vez y llama a uno.

**Salida detallada** — herramienta `archive_check`, entrada:

```json
{"fonds":"某单位","year":2026,"items":[{"档号":"A-2026-001","题名":"","保管期限":"永久", ...}]}
```

Salida:

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

*Observado en `dsh-archive-check/tests/fixtures/AR-001/AR-001-unsafe.json; dsh-archive-check/tests/fixtures/AR-001/cases.json; dsh-archive-check/rules/archive-check.yaml; dsh-archive-check/tests/index.test.ts`*

### Qué responde

| Usted pregunta | Qué responde |
|---|---|
| No he configurado ningún campo de descripción obligatorio. ¿La comprobación de la descripción pasa en silencio? | No. Mientras `requiredFields` esté vacío, `AR-001` se declara en `skipped`, de modo que una lista de diferencias vacía no se lee como «no falta nada». Cuando indique los nombres de sus columnas, solo comprueba que cada campo esté relleno en cada asiento —una cadena vacía cuenta como no relleno— y no juzga si la descripción es exacta. |
| Dos asientos llevan el mismo 档号, pero uno tiene un espacio en medio. ¿Sigue siendo duplicado? | Sí. `AR-002` compara el 档号 ignorando los espacios, así que 「A-2026-001」 y 「A-2026- 001」 cuentan como el mismo número. Está limitado a `warn` porque la cláusula que cita enuncia la unicidad como principio de elaboración, y no como una prohibición literal de repetir dentro de un mismo registro; un hallazgo suele significar un registro duplicado o un 档号 mal escrito, que aún debe confirmar una persona. |
| La columna 保管期限 dice algo que nuestra tabla de plazos no recoge. ¿Qué informa la comprobación? | `AR-003` separa dos casos: un valor que el analizador no reconoce como plazo (reconoce 「永久」「长期」「定期N年」「N年」) y un término reconocible que no está en la lista `retentionTerms` que usted configure. Las correcciones son distintas, por eso los mensajes son distintos. La regla nunca decide qué plazo merece un documento, y un plazo más largo que el marco nacional no es un error: las disposiciones que cita el paquete fijan las cifras de empresa como mínimo. |
| Los 件号 son 1, 2, 4 — ¿se informa del 3 que falta? | Sí, pero solo para 件号 escritos con dígitos puros: `AR-004` comprueba la continuidad únicamente en esos casos; un 件号 con letras o espacios queda fuera de la comparación y no informa de ninguna diferencia. Un hueco no es por sí mismo un defecto —puede que ese número no se haya usado—, así que el hallazgo solo pide confirmar si algún asiento quedó sin registrar. Con `checkSequence: false` la regla no se ejecuta. |
| El 形成日期 figura como 「二〇二六年三月十五日」. ¿Se lee? | No. `AR-005` lo informa como «no se puede analizar», que es un mensaje distinto del de una fecha cuyo año no coincide con el año del registro: apuntan a correcciones diferentes. Archivar entre años está permitido, y la regla no decide en qué año debería figurar un documento. |
| ¿Cómo sabe la comprobación que ya toca transferir? | `AR-007` compara el 形成日期 de cada asiento con el `transferAfterYears` que usted configure e informa solo de si ese plazo ya venció según los años fijados. El parámetro sale de fábrica como `0`, es decir, sin configurar, así que la regla se declara en `skipped` hasta que usted lo fije; con `requireFormedAt: true` también se informa por separado de los asientos sin 形成日期, porque no hay fecha desde la que calcular el vencimiento. La regla no juzga si la transferencia debería adelantarse o aplazarse. |

## Configuración

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`. Las cinco claves de la tabla son la lista completa; los parámetros por regla vienen después.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/archive-check.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

Parámetros por regla que conviene conocer:

- `AR-001` `requiredFields` — las columnas que cada fila debe rellenar, p. ej. `[档号, 题名, 保管期限, 责任者]`. Vacío significa que la regla no se ejecuta. Una celda en blanco cuenta como no rellena.
- `AR-003` `retentionTerms` — los términos que usa tu tabla de plazos, p. ej. `[永久, 定期30年, 定期10年]`; también puede pasarse por llamada para una comparación puntual.
- `AR-004` `checkSequence` — ponlo en `false` para dejar de comprobar la continuidad de los 件号.
- `AR-006` `requireHeader` — ponlo en `false` si tu registro legítimamente no lleva fondo ni año.
- `AR-007` `transferAfterYears` — el plazo de transferencia de **tu** archivo: `20` para un archivo receptor central / provincial / subprovincial, `10` para uno de nivel de condado (según el reglamento de aplicación citado). `0` significa que la regla no se ejecuta. `AR-007` `requireFormedAt` convierte una columna 形成日期 ausente en un hallazgo en lugar de una omisión, porque sin fecha no se puede calcular el vencimiento.

## FAQ

<details>
<summary>¿Mi material se modifica o se sube a algún sitio?</summary>

No. La herramienta solo lee el texto JSON/YAML que le entregas y **nunca modifica el original**; el plugin es ESM puro, sin código nativo, **sin red y sin llamada al modelo** (véase Compatibilidad), así que el material nunca sale de tu máquina.

</details>

<details>
<summary>Sin campos obligatorios ni tabla configurados, ¿algo pasa en silencio?</summary>

No. Las dos listas —`requiredFields` de `AR-001` y `retentionTerms` de `AR-003`— salen de fábrica vacías, y una regla cuya lista no está configurada se declara en `skipped` con el motivo, así que una lista de diferencias vacía nunca se lee como «no falta nada». `AR-003` también puede alimentarse por llamada para una comparación puntual sin editar el paquete de reglas.

</details>

<details>
<summary>El plugin se instala pero la herramienta nunca aparece — ¿qué hago?</summary>

Comprueba que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó; un `main` erróneo hace que el cargador se salte la entrada en silencio.

</details>

<details>
<summary>La instalación se rechaza por versión incompatible — ¿qué hago?</summary>

El rango de peers cubre las líneas `0.1.x` y `0.2.x`; si tu runtime queda fuera, concede una exención explícita: `dsh plugin --profile <name> allow-version dsh-archive-check@0.1.0 --dsh-version <runtime> --accept-risk`. La compatibilidad de peers la aplica el runtime al instalar.

</details>

<details>
<summary>¿Puede con un año entero de registros o con un directorio completo?</summary>

La herramienta funciona en modo `native` y `ptc`; para un año de registros usa `ptc`, así el coste del esquema se paga una sola vez. Toda la aritmética es de hora local sobre las cadenas entregadas, sin conversión de zonas horarias.

</details>

## Normas que sigue

| Documento | Número | Reglas que lo citan |
|---|---|---|
| 《归档文件整理规则》 | DA/T 22—2015 | AR-001, AR-002, AR-004, AR-005, AR-006 |
| 《中华人民共和国档案法实施条例》 | 国务院令第772号 | AR-001, AR-003, AR-007 |
| 《机关文件材料归档范围和文书档案保管期限规定》 | 国家档案局令第8号 | AR-003 |
| 《企业文件材料归档范围和档案保管期限规定》 | 国家档案局令第10号 | AR-003 |
| 《中华人民共和国档案法》 | 2020年修订（主席令第四十七号） | AR-007 |

**Límite:** este plugin comprueba un **归档登记表** (registro de archivo) en lo que un registro puede sostener mecánicamente: que cada asiento esté descrito con la suficiente completitud para ser archivado y recuperado, que el 档号 sea único, que el 件号 corra sin huecos, que los plazos vengan de tu tabla y que el 形成日期 se pueda analizar y coincida con el año del registro. **No** decide si un documento concreto debía archivarse ni qué plazo merece. Esas son decisiones del archivero.

> ### ⚠️ Tres cosas que este plugin se niega a hacer, y por qué
>
> **1. Nunca decide qué plazo de conservación merece un documento.** No existe **una tabla nacional
> única de plazos** que puedas aplicar. El reglamento de aplicación (artículo 19, segundo párrafo) y
> la Orden n.º 8 (artículo 12) exigen que cada institución elabore su propio alcance de archivo y su
> propia tabla de plazos y la someta a la aprobación de la autoridad archivística; y la Orden n.º 10
> (artículo 11) dice que las cifras para empresas son un **mínimo** —una empresa puede elegir
> legalmente un plazo *más largo*. Por eso `AR-003` solo comprueba que la redacción sea una de las
> que tú configuraste, y un test garantiza que el paquete dice que un plazo más largo «no es un error».
>
> **2. Sitúa los años de transferencia donde pertenecen.** Las cifras de 20 / 10 años están en el
> reglamento de aplicación (artículo 20, segundo párrafo), vinculadas al *nivel del archivo receptor*,
> no a si la unidad es una empresa. El artículo 15 de la Ley de Archivos **no contiene cifra alguna** —
> solo dice «según las disposiciones estatales pertinentes, periódicamente». Atribuir «20 años» al
> artículo 15 sería una fabricación, y un test garantiza que el paquete no lo hace.
>
> **3. No usa el primer artículo ya obsoleto.** El artículo 1 de la Orden n.º 8 cita las medidas de
> aplicación de 1999, que el reglamento de 2024 (Orden del Consejo de Estado n.º 772) derogó en su
> artículo 52. El paquete nunca lo cita, y un test lo garantiza.
>
> Hay dos listas que son tuyas, no de la ley: los campos de descripción obligatorios (`AR-001`) y tu
> vocabulario de plazos (`AR-003`). Ambas salen de fábrica **vacías**, y una regla cuya lista no está
> configurada se declara en `skipped` en lugar de pasar en silencio.

## Formato del material

La herramienta acepta JSON o YAML:

```yaml
fonds: 某单位
year: 2026
items:
  - { 档号: A-2026-001, 题名: 关于第一项工作的通知, 保管期限: 永久,   形成日期: 2026-03-15, 件号: "1" }
  - { 档号: A-2026-002, 题名: 关于第二项工作的通知, 保管期限: 定期30年, 形成日期: 2026-04-01, 件号: "2" }
```

Los nombres de columna se reconocen entre `档号`/`档案号`, `题名`/`文件题名`/`标题`, `保管期限`/`期限`, `形成日期`/`成文日期`/`日期` y `件号`/`序号`. Una simple lista de títulos también sirve: cada cadena se convierte en el 题名 de un asiento. Los números se aceptan como cadenas, así que una exportación de hoja de cálculo no necesita limpieza.

El 保管期限 se lee en dos formas: `永久`/`长期` para permanente, y cualquier `N年`/`定期N年`/`N` a secas para plazo fijo. Un término ilegible se informa como ilegible, lo cual es distinto de un término fuera de tu lista configurada: producen hallazgos diferentes, porque necesitan correcciones diferentes.

## Fuentes de las reglas

Los datos de las reglas viven en `rules/archive-check.yaml`, separados del código. Cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y la URL de donde se leyó. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada solo en un principio general o en una política local **nunca** se declare `error`.

Las cláusulas citadas provienen de:

- **《中华人民共和国档案法》** (revisión del 2020-06-20, 主席令第四十七号, en vigor desde 2021-01-01) — artículos 13–15, 21, 37, 39
- **《中华人民共和国档案法实施条例》** (**国务院令第772号**, publicada el 2024-01-12, **en vigor desde 2024-03-01**; su artículo 52 deroga las medidas de aplicación de 1999) — artículos 19, 20, 24, 39, 40
- **《机关文件材料归档范围和文书档案保管期限规定》** (国家档案局令第8号) — artículos 3, 4, 6, 12, 14
- **《企业文件材料归档范围和档案保管期限规定》** (国家档案局令第10号) — artículos 7, 11, 15, 16
- **《归档文件整理规则》** (DA/T 22—2015) — 5.2.2, 5.3.1, 5.4.1, 5.4.3 e), 5.5.2

Tres correcciones dieron forma a este paquete y quedaron registradas en su cabecera:

1. **El reglamento fue reemplazado.** La Orden del Consejo de Estado n.º 772 está en vigor desde 2024-03-01 y deroga las medidas de 1999, así que el artículo 1 de la Orden n.º 8 (que cita el texto derogado) nunca se cita.
2. **Los años de transferencia están en el reglamento, no en la ley.** El artículo 20, segundo párrafo, lleva las cifras de 20/10 años y las vincula al nivel del archivo receptor; el artículo 15 de la Ley de Archivos no tiene cifra alguna.
3. **No existe una tabla de plazos universal.** Cada institución elabora la suya y la somete a aprobación, y las cifras de empresa son un mínimo legal, no un techo.

El informe completo de verificación de cláusulas, incluidas las fuentes revisadas y descartadas, está en `rules/evidence/clause-verification.md`.

## Compatibilidad

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-rc.2`. `engines.dsh` se declara como `>=0.2.1-0 <0.3.0` y el host lo aplica desde 0.2.1 |
| Node | `^22.19.0 \|\| >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native` y `ptc`; para un año de registros usa `ptc` |

## Solución de problemas

- **`AR-001` y `AR-003` se declaran en `skipped`.** Sus listas están vacías. `AR-003` también puede alimentarse por llamada, así que una comparación puntual no necesita editar el paquete de reglas.
- **`AR-004` no informa de nada.** Menos de dos 件号 se analizaron como enteros puros: las referencias alfanuméricas se dejan fuera de la comprobación de continuidad deliberadamente, en lugar de adivinarse.
- **`AR-005` salta sobre una fecha que sí puedo leer.** El lector acepta `2026-03-15` y `2026-03-15 09:30`; una fecha en numerales chinos se informa como no analizable a propósito, para que decidas si normalizar la exportación.
- **El lector rechaza un registro que antes aceptaba.** No encontró ninguna de las columnas de archivo conocidas; el error nombra las columnas que vio.
- **El plugin se instala pero la herramienta nunca aparece.** Comprueba que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó; un `main` erróneo hace que el cargador se salte la entrada en silencio.
- **`dsh plugin add` rechaza el paquete como incompatible.** El rango de peers cubre `0.1.x` y `0.2.x`; si tu runtime queda fuera, concede una exención explícita: `dsh plugin --profile <name> allow-version dsh-archive-check@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` informa `manifest-peers` como fallo.** El comprobador estático compara contra un rango de peers fijado en código anterior a la línea 0.2. El runtime aplica la compatibilidad al instalar, así que el rango declarado es el correcto; es un problema conocido de `dsh-plugin-dev`.
- **Los horarios parecen desplazados.** Toda la aritmética es de hora local sobre las cadenas entregadas, sin conversión de zonas horarias.

## Ecosistema y calidad

- [Espejo de Gitee](https://gitee.com/perrylink/dsh-archive-check) (espejo sincronizado; GitHub es el canónico)
- [Página del plugin en dshfind](https://dshfind.com/plugins/PerryLink/dsh-archive-check) (instalaciones y ranking)
- [Informe de OpenSSF Scorecard](https://securityscorecards.dev/viewer/?uri=github.com/PerryLink/dsh-archive-check) (impulsado por [.github/workflows/scorecard.yml](.github/workflows/scorecard.yml))
- [DSH Market](https://dsh.market/) (listado)
- [Base de conocimiento del ecosistema — elige un verificador por material](https://perrylink.github.io/zh/checkers/choose/) (índice completo de la familia: 62 verificadores + plugins generales)

## Desarrollo

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, fixtures emparejados por regla (tests/fixtures/<RULE>/)
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
pnpm run check:readmes   # consistencia de los README en cinco idiomas
node ../scripts/sync-shared.mjs dsh-archive-check   # refresca src/shared desde ../_shared
```

El paquete de reglas es dato, no código: edita `rules/*.yaml` para cambiar el conjunto de reglas sin tocar TypeScript; el paquete se valida al cargar, no se confía en él. Las imágenes del README se generan programáticamente con [`scripts/gen-readme-assets.py`](scripts/gen-readme-assets.py) (Pillow para el hero localizado y un SVG escrito a mano para la figura de estructura) y pueden reejecutarse sin riesgo; este plugin no tiene UI y la figura de estructura solo usa tokens de la superficie de comandos, identificadores de reglas/campos/cláusulas y breves leyendas en inglés.

Topics: `dsh`, `dsh-plugin`, `deepseek-harness`, `cordis`, `archive`

## Familia y agradecimientos

Este proyecto forma parte de la familia de plugins de DeepSeek Harness de [PerryLink](https://github.com/PerryLink) (todos Apache-2.0). Si te resulta útil, **una estrella** no desbloquea nada, pero ayuda a que la siguiente persona lo encuentre.

- [@PerryLink](https://github.com/PerryLink) — creador y mantenedor: la herramienta `archive_check`, el paquete de reglas con citas literales y su registro de verificación de cláusulas, y la documentación en cinco idiomas.

<details>
<summary>Expandir todos los plugins</summary>

| Plugin | Estado |
|---|---|
| **[dsh-aqua-input-check](https://github.com/PerryLink/dsh-aqua-input-check)** |  |
| **[dsh-archive-check](https://github.com/PerryLink/dsh-archive-check)** |  |
| **[dsh-auto-review](https://github.com/PerryLink/dsh-auto-review)** |  |
| **[dsh-autotier](https://github.com/PerryLink/dsh-autotier)** | 🧊 CONGELADO — ver el README del repo |
| **[dsh-bid-ca-precheck](https://github.com/PerryLink/dsh-bid-ca-precheck)** |  |
| **[dsh-bid-qual-check](https://github.com/PerryLink/dsh-bid-qual-check)** |  |
| **[dsh-cert-mcp](https://github.com/PerryLink/dsh-cert-mcp)** | 🧊 CONGELADO — ver el README del repo |
| **[dsh-checkpoint-rewind](https://github.com/PerryLink/dsh-checkpoint-rewind)** |  |
| **[dsh-click](https://github.com/PerryLink/dsh-click)** |  |
| **[dsh-composer-history](https://github.com/PerryLink/dsh-composer-history)** |  |
| **[dsh-contract-stance](https://github.com/PerryLink/dsh-contract-stance)** |  |
| **[dsh-customs-doc-check](https://github.com/PerryLink/dsh-customs-doc-check)** |  |
| **[dsh-data-quality](https://github.com/PerryLink/dsh-data-quality)** | 🧊 CONGELADO — ver el README del repo |
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
| **[dsh-memento](https://github.com/PerryLink/dsh-memento)** | 🧊 CONGELADO — ver el README del repo |
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
| **[dsh-plugin-doctor](https://github.com/PerryLink/dsh-plugin-doctor)** | 🚫 RETIRADO (repo archivado) |
| **[dsh-plugin-guide](https://github.com/PerryLink/dsh-plugin-guide)** |  |
| **[dsh-plugin-kit](https://github.com/PerryLink/dsh-plugin-kit)** | 🚫 RETIRADO (repo archivado) |
| **[dsh-plugin-upgrade](https://github.com/PerryLink/dsh-plugin-upgrade)** | 🚫 RETIRADO (repo archivado) |
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
| **[dsh-score](https://github.com/PerryLink/dsh-score)** | 🧊 CONGELADO — ver el README del repo |
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
| **[dsh-ticktick](https://github.com/PerryLink/dsh-ticktick)** | 🚫 RETIRADO (repo archivado) |
| **[dsh-translate](https://github.com/PerryLink/dsh-translate)** |  |
| **[dsh-warranty-calc](https://github.com/PerryLink/dsh-warranty-calc)** |  |
| **[dsh-budget](https://github.com/PerryLink/dsh-budget)** | 🧊 CONGELADO — ver el README del repo |
| **[dsh-claude-move](https://github.com/PerryLink/dsh-claude-move)** | 🧊 CONGELADO — ver el README del repo |
| **[dsh-defend](https://github.com/PerryLink/dsh-defend)** | 🧊 CONGELADO — ver el README del repo |
| **[dsh-draw](https://github.com/PerryLink/dsh-draw)** | 🧊 CONGELADO — ver el README del repo |
| **[dsh-reach](https://github.com/PerryLink/dsh-reach)** | 🧊 CONGELADO — ver el README del repo |
| **[dsh-background-agents](https://github.com/PerryLink/dsh-background-agents)** | 🚫 RETIRADO (repo archivado) |
| **[dsh-session-pin](https://github.com/PerryLink/dsh-session-pin)** | 🚫 RETIRADO (repo archivado) |
| **[dsh-team-rooms](https://github.com/PerryLink/dsh-team-rooms)** | 🚫 RETIRADO (repo archivado) |

</details>

## Licencia

[LICENSE](LICENSE) (Apache License 2.0) © 2026 dsh-archive-check contributors

<p align="center"><sub>Apache-2.0 · Plugin de la comunidad, no afiliado a DeepSeek.</sub></p>
