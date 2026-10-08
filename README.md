# dsh-archive-check

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

| Surface | Status |
|---|---|
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-alpha.1`. `engines.dsh` is deliberately not declared: it has no reader and cannot reject a host |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native`, `ptc` and `both`; for a year's registers use `ptc` |

## What it does

Registers the `archive_check` tool. It reads one register — items with the columns the register carries,
plus the fonds and year it covers — applies a versioned rule pack, and returns a report.

| Rule | Check | Severity | Basis kind |
|---|---|---|---|
| `AR-001` | each item carries your required description fields (off by default) | info | local |
| `AR-002` | 档号 is unique within the register | warn | principle |
| `AR-003` | 保管期限 uses a term from your schedule (off by default) | info | local |
| `AR-004` | 件号 is unique and gap-free within the register | warn | principle |
| `AR-005` | 形成日期 parses, and its year matches the register's year | warn | principle |
| `AR-006` | the register declares its fonds and year | warn | principle |
| `AR-007` | items past your configured transfer deadline (off by default) | info | local |

## Install

```sh
dsh plugin --profile <name> add dsh-archive-check
dsh --profile <name> --dump-config | grep 'dsh-archive-check'
```

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `rulesFile` | string | `rules/archive-check.yaml` | Rule-pack path, relative to the package root |
| `disabledRules` | string[] | `[]` | Rule ids to stop running; each appears in `skipped` |
| `onlyRules` | string[] | `[]` | Run only these rule ids; empty runs every rule |
| `skipNotes` | string | `""` | Note appended to every `skipped` reason |
| `timeoutMs` | number | `120000` | Cooperative tool timeout budget |

Rule-level parameters worth knowing:

- `AR-001` `requiredFields` — the columns a row must fill, e.g. `[档号, 题名, 保管期限, 责任者]`.
  Empty means the rule does not run. A blank cell counts as unfilled.
- `AR-003` `retentionTerms` — the terms your 保管期限表 uses, e.g.
  `[永久, 定期30年, 定期10年]`. It can also be passed per call for a one-off comparison.
- `AR-004` `checkSequence` — set to `false` to stop checking 件号 continuity.
- `AR-006` `requireHeader` — set to `false` if your register legitimately carries no fonds or year.
- `AR-007` `transferAfterYears` — **your** archive's transfer deadline: `20` for a central / provincial /
  sub-provincial receiving archive, `10` for a county-level one (《档案法实施条例》第二十条第二款).
  `0` means the rule does not run. `AR-007` `requireFormedAt` makes a missing 形成日期 column a finding
  rather than a skip, because the deadline cannot be computed without it.

## Material format

The tool accepts JSON or YAML:

```yaml
fonds: 某单位
year: 2026
items:
  - { 档号: A-2026-001, 题名: 关于第一项工作的通知, 保管期限: 永久,   形成日期: 2026-03-15, 件号: "1" }
  - { 档号: A-2026-002, 题名: 关于第二项工作的通知, 保管期限: 定期30年, 形成日期: 2026-04-01, 件号: "2" }
```

Column names are recognised from `档号`/`档案号`, `题名`/`文件题名`/`标题`, `保管期限`/`期限`,
`形成日期`/`成文日期`/`日期`, and `件号`/`序号`. A plain list of titles also works — each string
becomes an item's 题名. Numbers are accepted as strings, so a spreadsheet export needs no cleaning.

`保管期限` is read in two shapes: `永久`/`长期` for permanent, and any `N年`/`定期N年`/bare `N` for a
fixed term. A term it cannot read is reported as unreadable, which is different from a term outside your
configured list — the two produce different findings, because they need different fixes.

## Rule sources

Rule data lives in `rules/archive-check.yaml`. Every rule carries a document, a document number, a
clause in the source's own numbering, a verbatim excerpt and the URL the excerpt was read from. The
loader enforces that an excerpt is a real quotation of at least eight characters, and that a check
resting on a general principle or a local policy can never be declared `error`.

The clauses quoted come from:

- **《中华人民共和国档案法》** (2020-06-20 revision, 主席令第四十七号, in force 2021-01-01) — articles 13–15, 21, 37, 39
- **《中华人民共和国档案法实施条例》** (**国务院令第772号**, published 2024-01-12, **in force 2024-03-01**;
  its 第五十二条 repeals the 1999 《档案法实施办法》) — articles 19, 20, 24, 39, 40
- **《机关文件材料归档范围和文书档案保管期限规定》** (国家档案局令第8号) — articles 3, 4, 6, 12, 14
- **《企业文件材料归档范围和档案保管期限规定》** (国家档案局令第10号) — articles 7, 11, 15, 16
- **《归档文件整理规则》** (DA/T 22—2015) — 5.2.2, 5.3.1, 5.4.1, 5.4.3 e), 5.5.2

Three corrections shaped this pack and are recorded in its header:

1. **The regulation was replaced.** 国务院令第772号 is in force from 2024-03-01 and repeals the 1999
   implementation measures, so 令第8号's 第一条 (which cites the repealed text) is never quoted.
2. **The transfer years live in the regulation, not the law.** 第二十条第二款 carries the 20/10 year
   figures and keys them to the receiving archive's level; 《档案法》第十五条 has no year at all.
3. **No universal retention table exists.** Each institution compiles and has its own approved, and an
   enterprise's figures are a statutory minimum rather than a ceiling.

The full clause-verification report, including the sources that were checked and rejected, is in
`rules/evidence/clause-verification.md`.

## Troubleshooting

- **`AR-001` and `AR-003` report themselves as skipped.** Their lists are empty. `AR-003` can also be fed
  per call, so a one-off comparison needs no rule-pack edit.
- **`AR-004` reports nothing.** Fewer than two 件号 values parsed as plain integers — alphanumeric
  references are deliberately left out of the continuity check rather than guessed at.
- **`AR-005` fires on a date I can read.** The reader accepts `2026-03-15` and `2026-03-15 09:30`; a
  Chinese-numeral date like `二〇二六年三月十五日` is reported as unparseable on purpose, so you can
  decide whether to normalise the export.
- **The reader refuses a register it used to accept.** It found none of the known archive columns; the
  error names the columns it saw.
- **The plugin installs but the tool never appears.** Check that `main` resolves to `lib/index.mjs` and
  that `pnpm run build` produced it; a wrong `main` makes the loader skip the entry silently.
- **`dsh plugin add` refuses the package as incompatible.** The peer range covers `0.1.x` and `0.2.x`;
  if your runtime sits outside it, grant an explicit exemption:
  `dsh plugin --profile <name> allow-version dsh-archive-check@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` reports `manifest-peers` as failed.** The static checker compares against a hard-coded peer
  range that predates the 0.2 line. The runtime enforces peer compatibility at install time, so the
  declared range is the correct one; this is a known upstream issue in `dsh-plugin-dev`.

## Development

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, paired fixtures per rule
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
node ../scripts/sync-shared.mjs dsh-archive-check   # refresh src/shared from ../_shared
```

## License

[Apache License 2.0](LICENSE) © 2026 dsh-archive-check contributors.
