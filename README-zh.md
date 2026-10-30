# dsh-archive-check — 档案归档完整性与保管期限核对

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

<!-- topblock:v1 -->
> **这是什么**　档案归档完整性与保管期限核对。输出一份「哪一行、哪一栏、差什么」的清单。
> **给谁用**　档案员、办公室文秘；不用懂命令行。
> **你交什么**　这项核对用到的原始材料（表格、清单或文书）；不改原件。Excel 可先转成 JSON/YAML，对话里也能代转。
> **它不做什么**　不判合规、不认定责任、不替代审核人；只列材料内部能逐条指认的差异。
> **怎么开始**　在 WorkBuddy / 扣子搜「职业文档核对全集」（总包，本检查是其中一项；上架以商城为准）；或命令行：
> `dsh plugin --profile <name> add dsh-archive-check`
<!-- /topblock:v1 -->

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)
[![dshfind](https://dshfind.com/api/badge/PerryLink/dsh-archive-check?metric=downloads)](https://dshfind.com/en/plugins/PerryLink/dsh-archive-check?ref=badge)

`dsh-archive-check` 读取一份归档登记表——登记表自带的栏目逐条列出，加上它所覆盖的全宗与年度——核对登记表自身可以机械判定的事项：每条是否填写了本机构配置的著录栏目、档号在同一登记范围内是否唯一、件号是否连续无缺号、保管期限是否使用本机构期限表的用词、形成日期是否可解析并与登记年度一致，以及是否报出已过本机构配置的移交期限的条目。

## 实际输出长什么样

![dsh-archive-check 工作流图：文档 → 规则包 → 核对结果。](docs/assets/dsh-archive-check-flow.svg)

*工作流概览：文档 → 规则包 → 核对结果。下面的示例使用实际命令面。*


本插件对自己 `AR-002` 测试夹具的**真实输出**，不是示意图。规则库不伪造引文，因此每条发现都会同时写明所引条款，以及该条款原文本次未取得。

## 它回答什么问题

### 示例

下表是示例集：第一行是详细走查，其余行是简短案例。


#### 详细输出

**工具** `archive_check`

**输入**

~~~json
{"fonds":"某单位","year":2026,"items":[{"档号":"A-2026-001","题名":"","保管期限":"永久", ...}]}
~~~
 
**输出**

~~~json
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
~~~

*来源 `dsh-archive-check/tests/fixtures/AR-001/AR-001-unsafe.json; dsh-archive-check/tests/fixtures/AR-001/cases.json; dsh-archive-check/rules/archive-check.yaml; dsh-archive-check/tests/index.test.ts`*

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

**边界（中文译文，以英文原文为准）：** 本插件核对一份**归档登记表**，范围限于登记表可以机械判定的事项——每条是否著录得足够完整，能够被归档并再次查到，档号是否唯一，件号是否连续无缺号，保管期限用词是否取自本机构的期限表，形成日期是否可解析并与登记年度一致。它**不**判定某份文件是否应当归档，也不判定其应为何种保管期限——那些是档案人员的判断。

> ### ⚠️ 本插件拒绝做的三件事及理由（以英文原文为准）
>
> **1. 它从不判定一份文件应适用哪个保管期限。** 不存在可供你直接套用的**单一国家保管期限表**。
> 《档案法实施条例》第十九条第二款与国家档案局令第8号第十二条要求各机构自行编制其归档范围与
> 保管期限表，并报档案主管部门批准；国家档案局令第10号第十一条规定，企业相关数字是**最低要求**——
> 企业可以合法选择*更长*的期限。因此，`AR-003` 只核对措辞是否为你所配置的措辞，并有测试断言
> 规则包写明更长期限“不是错误”。
>
> **2. 它把移交年限放在其应属的位置。** 20 年 / 10 年这两个数字出自
> **《档案法实施条例》第二十条第二款**，对应的是*接收档案馆的级别*，而不是该单位是否为企业。
> 《档案法》第十五条**完全没有年限数字**——它只说“按照国家有关规定，定期”。把“满20年”归到该法
> 第十五条会构成伪造，并有测试断言规则包不会这样做。
>
> **3. 它不使用过时的第一条。** 国家档案局令第8号的第一条援引 1999 年《档案法实施办法》，
> 而 2024 年条例（国务院令第772号）已在第五十二条废止该办法。规则包从不援引它，并有测试对此
> 作出断言。
>
> 有两份清单是你的，而不是法律规定的：必填著录字段（`AR-001`）与你的保管期限词汇表（`AR-003`）。
> 两者出厂均为**空**，清单未配置的规则会在 `skipped` 中自行报告，而不是静默通过。

## Compatibility

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-rc.2`。**已声明 `engines.dsh`**：0.2.1 起由宿主单独裁决，范围为 `>=0.2.1-0 <0.3.0` |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

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

## PerryLink DSH Plugin Family

完整清单（62 个核查器 + 通用插件）见 [按材料选核查器](https://perrylink.github.io/zh/checkers/choose/)；本仓只是其中一个。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-archive-check contributors.
