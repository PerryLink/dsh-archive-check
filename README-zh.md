# dsh-archive-check — 档案归档完整性与保管期限核对

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-archive-check` 读取一份归档登记表——登记表自带的栏目逐条列出，加上它所覆盖的全宗与年度——核对登记表自身可以机械判定的事项：每条是否填写了本机构配置的著录栏目、档号在同一登记范围内是否唯一、件号是否连续无缺号、保管期限是否使用本机构期限表的用词、形成日期是否可解析并与登记年度一致，以及是否报出已过本机构配置的移交期限的条目。

## 实际输出长什么样

![Terminal demo of dsh-archive-check: real output over its AR-002 fixture](https://raw.githubusercontent.com/PerryLink/dsh-archive-check/main/docs/assets/dsh-archive-check-demo.png)

本插件对自己 `AR-002` 测试夹具的**真实输出**，不是示意图。规则库不伪造引文，因此每条发现都会同时写明所引条款，以及该条款原文本次未取得。

## 它回答什么问题

| 你会问 | 它怎么答 |
|---|---|
| 我没有配置必填的著录栏目，著录核对会静默通过吗？ | 不会。`requiredFields` 为空时，`AR-001` 会把自己报进 `skipped`，因此空的差异清单不会被读成「没有缺项」。填入本机构的栏目名之后，它只核对每条是否填写了这些栏目（空串视为未填），不判断著录内容是否准确。 |
| 两条的档号相同，但其中一条中间多了空格，还算重复吗？ | 算。`AR-002` 比较时忽略空白字符，「A-2026-001」与「A-2026- 001」视为同一档号。本条封顶为 `warn`，因为它所引条款把「唯一性」写成编制原则，而不是「同一登记表内不得重复」的逐字规定；命中通常意味着重复登记或档号填错，仍需人工确认。 |
| 保管期限栏写的是本机构期限表里没有的用词，会报出什么？ | `AR-003` 把两种情况分开：完全识别不了的期限用词（可识别的是「永久」「长期」「定期N年」「N年」），与能被识别但不在本机构配置的 `retentionTerms` 清单内的用词。两者的改法不同，因此报出的是两条不同的信息。本条绝不判定某份文件应为何期限；期限高于国家框架也不是错误，规则库所引规定把企业期限写作最低期限。 |
| 件号是 1、2、4，缺了 3，会被报出来吗？ | 会，但只限纯数字件号：`AR-004` 只对纯数字件号做连续性核对，含字母或空格的件号不参与比较，也不会报出任何差异。缺号本身不构成问题——可能该号未使用——因此命中只提示核对是否有条目漏登记。`checkSequence: false` 时本条不执行。 |
| 形成日期写成「二〇二六年三月十五日」，读得出来吗？ | 读不出来。`AR-005` 会报「无法解析」，这与「年度与登记年度不一致」是两条不同的信息，对应两种不同的改法。跨年度归档是允许的，本条不判断该文件应归入哪一年。 |
| 移交期限到没到，插件是怎么算的？ | `AR-007` 把每条的形成日期与本机构配置的 `transferAfterYears` 相比，只报出按该年限是否已经到期。该参数出厂为 `0`，表示未配置，因此在配置之前本条会把自己报进 `skipped`；把 `requireFormedAt` 设为 `true` 时，缺少形成日期的条目会单独报出，因为无从推算到期日。本条不判断是否应当延长或提前移交。 |

## 依据的标准

| 文件 | 文号 | 引用它的规则 |
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

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-alpha.1`。**刻意不声明 `engines.dsh`**：它没有任何读取者，也无法拒装任何宿主 |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` / `both` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Install

```sh
dsh plugin --profile <name> add dsh-archive-check
dsh --profile <name> --dump-config | grep 'dsh-archive-check'
```

## Configuration

全部可调参数都在 `src/config.ts` 的 Schemastery schema 中，只改 `cordis.yml` 即可生效，无需改代码；逐条阈值在 `rules/` 下的规则库文件里。

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rulesFile` | string | `rules/archive-check.yaml` | 规则库文件路径，相对插件包根目录 |
| `disabledRules` | string[] | `[]` | 要停用的规则 id 列表；每条都会出现在 `skipped` 中 |
| `onlyRules` | string[] | `[]` | 只执行这些规则 id；留空表示执行全部规则 |
| `skipNotes` | string | `""` | 附加到每条 `skipped` 说明后的备注 |
| `timeoutMs` | number | `120000` | 工具协作式超时预算（毫秒） |

## Material format

支持 JSON 与 YAML。完整字段示例见 [README.md](README.md#material-format)（英文主版本）。字段在读取层是可选的，由检查引擎校验，因此部分导出的材料会产生"缺项"类差异，而不是让程序崩溃。

## Rule sources

规则数据与代码分离，每条规则都带文件名、文号、按原文自身编号体系的条款号、逐字摘录与来源地址。加载期强制：摘录必须是真实引文且不少于八个字符；依据仅为原则性条款（`kind: derived-from-principle`，严重级上限 `warn`）或本机构配置（`kind: institutional-configuration`，上限 `info`）的检查不得标为 `error`。夸大依据的规则库会在加载期失败，而不会产出一份看起来很有底气的报告。

核验中确认的边界与"刻意没有作出的结论"见 [README.md](README.md#rule-sources)（英文主版本）与随包的 `rules/evidence/` 目录。

## Troubleshooting

- **插件装上了但工具不出现**：确认 `main` 指向 `lib/index.mjs` 且 `pnpm run build` 已生成该文件；`main` 写错会让加载器静默跳过该条目。
- **`dsh plugin add` 报版本不兼容**：peer 范围覆盖 `0.1.x` 与 `0.2.x`；若运行时在其之外，可显式豁免：`dsh plugin --profile <name> allow-version <包名@版本> --dsh-version <runtime> --accept-risk`
- **某条规则没有执行**：查看 `skipped` 数组，其中写明了规则 id 与原因。
- **`check` 报 `manifest-peers` 失败**：静态检查器比对的是一份早于 0.2 世代的硬编码 peer 范围；安装期的 peer 校验以运行时为准。这是 `dsh-plugin-dev` 的已知上游问题。
- **时间看起来偏移**：全部计算都是对输入字符串做墙上时钟运算，不做时区换算。

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-archive-check
```

第 4 项把 `../_shared` 的共享件同步进 `src/shared/`；每次改动共享件后都要重跑。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-archive-check contributors.
