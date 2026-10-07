/**
 * Pure check core: `(input, ruleset, options) => Report`.
 *
 * No plugin context, no I/O, no clock and no model access, so the whole rule set
 * is unit-testable without credentials. Every finding carries the verbatim clause
 * that produced it, and every check that could not run is reported in `skipped`
 * so an empty issue list can never be read as "nothing is wrong".
 *
 * The checks are about whether an item is **described well enough to be filed and
 * found again**, and whether the retention arithmetic is consistent. Deciding
 * whether a particular document belonged in the archive at all is the archivist's
 * judgement, and this plugin does not attempt it.
 */

import { disabledAsSkipped, formatBasis } from './shared/rules.ts'
import { paramNumber, paramStrings, ruleById } from './shared/ruleset.ts'
import { issueId, makeReport } from './shared/report.ts'
import { addDays, parseWallClock } from './shared/datetime.ts'
import { parseRetention } from './model.ts'
import type { Issue, Locator, Report, Skipped } from './shared/report.ts'
import type { Ruleset } from './shared/rules.ts'
import type { ArchiveInput, ArchiveItem } from './model.ts'

/** Options that come from the plugin configuration rather than the rule pack. */
export interface CheckOptions {
  plugin: string
  checkedAt: string
  disabledRules: readonly string[]
  onlyRules: readonly string[]
  /** Retention terms the deployment's schedule actually uses, e.g. ['永久', '定期30年']. */
  retentionTerms?: readonly string[]
  skipNotes?: string
}

interface RuleContext {
  input: ArchiveInput
  ruleset: Ruleset
  issues: Issue[]
  skipped: Skipped[]
  fired: Set<string>
  skipReasons: Map<string, string>
  options: CheckOptions
  add(ruleId: string, locator: Locator, found: string, expected: string, fix?: string): void
  skip(ruleId: string, reason: string): void
}

function locatorOf(item: ArchiveItem, column?: string): Locator {
  const locator: Locator = { row: item.row }
  if (column !== undefined) locator.column = column
  return locator
}

function makeAdd(context: Omit<RuleContext, 'add' | 'skip'>): RuleContext['add'] {
  return (ruleId, locator, found, expected, fix) => {
    const rule = ruleById(context.ruleset, ruleId)
    const issue: Issue = {
      id: issueId(context.ruleset.plugin, ruleId, locator),
      ruleId,
      severity: rule.severity,
      locator,
      found,
      expected,
      basis: formatBasis(rule.basis, rule.alsoBasis ?? []),
    }
    if (fix !== undefined) issue.fix = fix
    context.issues.push(issue)
    context.fired.add(ruleId)
  }
}

/** AR-001 — each item carries the identifying description the register needs. */
function checkDescriptiveCompleteness(context: RuleContext): void {
  const ruleId = 'AR-001'
  const rule = ruleById(context.ruleset, ruleId)
  const required = paramStrings(rule, 'requiredFields', [])
  if (required.length === 0) {
    context.skip(
      ruleId,
      '规则库未配置 requiredFields：著录项目清单随《归档文件整理规则》版本与本单位细则变化，本插件不硬编码',
    )
    return
  }
  for (const item of context.input.items) {
    const missing = required.filter((field) => {
      const value = item.fields[field]
      return value === undefined || value.trim() === ''
    })
    if (missing.length === 0) continue
    context.add(
      ruleId,
      locatorOf(item),
      `第 ${item.row} 行缺少 ${missing.join('、')}`,
      `按本机构配置，归档条目应著录 ${required.join('、')}`,
      '补齐著录项目；本条只核对字段是否存在，不判断著录内容是否准确',
    )
  }
}

/** AR-002 — 档号 is unique within the register. */
function checkReferenceUnique(context: RuleContext): void {
  const ruleId = 'AR-002'
  const seen = new Map<string, ArchiveItem>()
  const duplicates: { item: ArchiveItem; first: ArchiveItem }[] = []
  let counted = 0
  for (const item of context.input.items) {
    const reference = item.reference?.replace(/\s+/g, '')
    if (reference === undefined || reference === '') continue
    counted += 1
    const previous = seen.get(reference)
    if (previous === undefined) seen.set(reference, item)
    else duplicates.push({ item, first: previous })
  }
  if (counted === 0) {
    context.skip(ruleId, '材料中没有档号列，无法核对唯一性')
    return
  }
  for (const duplicate of duplicates) {
    context.add(
      ruleId,
      locatorOf(duplicate.item, '档号'),
      `档号「${duplicate.item.reference}」在第 ${duplicate.first.row} 行与第 ${duplicate.item.row} 行重复出现`,
      '同一全宗内档号应唯一',
      '核对是否重复登记，或其中一行的档号需要更正',
    )
  }
}

/** AR-003 — the retention period is one the schedule uses. */
function checkRetentionTerm(context: RuleContext): void {
  const ruleId = 'AR-003'
  const rule = ruleById(context.ruleset, ruleId)
  const configured = context.options.retentionTerms ?? paramStrings(rule, 'retentionTerms', [])
  const withTerm = context.input.items.filter((item) => item.retention !== undefined)
  if (withTerm.length === 0) {
    context.skip(ruleId, '材料中没有保管期限列，无法核对期限用词')
    return
  }
  if (configured.length === 0) {
    context.skip(
      ruleId,
      '规则库与配置均未提供 retentionTerms：保管期限表由本机构按《机关文件材料归档范围和文书档案保管期限规定》编制，本插件不硬编码期限用词',
    )
    return
  }
  for (const item of withTerm) {
    if (parseRetention(item.retention) === undefined) {
      context.add(
        ruleId,
        locatorOf(item, '保管期限'),
        `保管期限「${item.retention}」不是可识别的期限用词`,
        `保管期限应为 ${configured.join(' / ')} 之一`,
        '核对期限用词是否与本单位保管期限表一致',
      )
      continue
    }
    const value = (item.retention ?? '').trim()
    if (configured.includes(value)) continue
    context.add(
      ruleId,
      locatorOf(item, '保管期限'),
      `保管期限「${value}」不在本机构配置的期限用词内（${configured.join(' / ')}）`,
      `保管期限应为 ${configured.join(' / ')} 之一`,
      '核对是否使用了本单位保管期限表之外的期限；本条不判断该文件应划为何种期限',
    )
  }
}

/** AR-004 — 件号 runs without gaps or repeats within the register. */
function checkSequence(context: RuleContext): void {
  const ruleId = 'AR-004'
  const rule = ruleById(context.ruleset, ruleId)
  if (rule.params.checkSequence === false) {
    context.skip(ruleId, '规则库配置为不核对件号连续性，本条不执行')
    return
  }
  const numbers: { item: ArchiveItem; value: number }[] = []
  for (const item of context.input.items) {
    const raw = item.sequence?.replace(/\s+/g, '')
    if (raw === undefined || raw === '') continue
    if (!/^\d+$/.test(raw)) continue
    numbers.push({ item, value: Number.parseInt(raw, 10) })
  }
  if (numbers.length < 2) {
    context.skip(ruleId, '可解析的件号少于 2 个，无法核对连续性')
    return
  }
  const values = numbers.map((entry) => entry.value)
  const seen = new Set<number>()
  for (const entry of numbers) {
    if (seen.has(entry.value)) {
      context.add(
        ruleId,
        locatorOf(entry.item, '件号'),
        `件号 ${entry.value} 出现多次`,
        '同一盒内件号应唯一且连续',
        '核对是否重复编号或漏编后补编',
      )
    }
    seen.add(entry.value)
  }
  const max = Math.max(...values)
  const min = Math.min(...values)
  const missing: number[] = []
  for (let value = min; value <= max; value++) {
    if (!seen.has(value)) missing.push(value)
  }
  if (missing.length === 0) return
  const first = numbers[0] as { item: ArchiveItem; value: number }
  context.add(
    ruleId,
    locatorOf(first.item, '件号'),
    `件号范围 ${min}~${max} 中缺 ${missing.length} 个号：${missing.slice(0, 20).join('、')}${missing.length > 20 ? ' 等' : ''}`,
    '同一盒内件号应连续',
    '核对是否漏登记；配件号不连续本身不构成问题，需人工确认',
  )
}

/** AR-005 — 形成日期 parses and belongs to the register's year. */
function checkFormedAt(context: RuleContext): void {
  const ruleId = 'AR-005'
  const withDate = context.input.items.filter((item) => item.formedAt !== undefined)
  if (withDate.length === 0) {
    context.skip(ruleId, '材料中没有形成日期列，无法核对日期')
    return
  }
  const unreadable: ArchiveItem[] = []
  for (const item of withDate) {
    const parsed = parseWallClock(item.formedAt ?? '')
    if (parsed === undefined) {
      unreadable.push(item)
      continue
    }
    if (context.input.year === undefined) continue
    const year = Number.parseInt(parsed.date.slice(0, 4), 10)
    if (year === context.input.year) continue
    context.add(
      ruleId,
      locatorOf(item, '形成日期'),
      `形成日期 ${parsed.date} 的年度与登记年度 ${context.input.year} 不一致`,
      '归档年度的登记应以该年度形成的文件为范围',
      '核对是否属于跨年度归档，或登记年度需要调整；本条不判断该文件应归入哪一年',
    )
  }
  for (const item of unreadable) {
    context.add(
      ruleId,
      locatorOf(item, '形成日期'),
      `形成日期「${item.formedAt}」无法解析为日期`,
      '形成日期应为可解析的年月日，如 2026-03-15 或 2026-03-15 09:30',
      '按本机构统一的日期写法填写',
    )
  }
}

/** AR-006 — the register's own header is declared. */
function checkHeader(context: RuleContext): void {
  const ruleId = 'AR-006'
  const rule = ruleById(context.ruleset, ruleId)
  if (rule.params.requireHeader === false) {
    context.skip(ruleId, '规则库配置为不要求登记表头，本条不执行')
    return
  }
  const missing: string[] = []
  if (context.input.fonds === undefined) missing.push('全宗名称或立卷单位')
  if (context.input.year === undefined) missing.push('年度')
  if (missing.length === 0) return
  context.add(
    ruleId,
    {},
    `登记表未声明 ${missing.join('、')}`,
    '归档登记表应能识别所属全宗与年度',
    '在材料顶层加入 fonds 与 year 字段',
  )
}

/**
 * AR-007 — has the configured transfer deadline passed?
 *
 * The statutory numbers live in the regulation's article 20 and are keyed to the
 * receiving archive's level, so the deployment supplies the number that applies to
 * it. An item formed more than that many years ago and still un-transferred is
 * reported; whether the transfer should be extended or brought forward is not a
 * question this plugin answers.
 */
function checkTransferDue(context: RuleContext): void {
  const ruleId = 'AR-007'
  const rule = ruleById(context.ruleset, ruleId)
  const years = paramNumber(rule, 'transferAfterYears', 0)
  if (years <= 0) {
    context.skip(
      ruleId,
      '规则库未配置 transferAfterYears：移交年限按档案馆层级区分（中央级/省级/设区的市级为20年、县级为10年，见《档案法实施条例》第二十条第二款），本插件不替使用方选定适用档位',
    )
    return
  }
  if (rule.params.requireFormedAt === true && context.input.items.every((item) => item.formedAt === undefined)) {
    context.add(
      ruleId,
      {},
      '按本机构配置需要核对移交期限，但材料中没有形成日期列',
      '推算移交到期日需要形成日期',
      '提供形成日期列，或关闭 requireFormedAt',
    )
  }
  const formed = context.input.items.filter((item) => item.formedAt !== undefined)
  if (formed.length === 0) {
    context.skip(ruleId, '材料中没有形成日期列，无法推算移交到期日')
    return
  }
  const cutoff = addDays(context.options.checkedAt.slice(0, 10), -years * 365)
  for (const item of formed) {
    const parsed = parseWallClock(item.formedAt ?? '')
    if (parsed === undefined) continue
    if (parsed.date > cutoff) continue
    context.add(
      ruleId,
      locatorOf(item, '形成日期'),
      `第 ${item.row} 行形成日期 ${parsed.date} 距核对日已满 ${years} 年（按 ${years}×365 天推算）`,
      `自档案形成之日起满 ${years} 年即应向有关国家档案馆移交`,
      '核对是否已办理移交或已获准延长；本条只按配置年限推算到期，不判断是否应当延长或提前移交',
    )
  }
}

const CHECKERS: readonly ((context: RuleContext) => void)[] = [
  checkDescriptiveCompleteness,
  checkReferenceUnique,
  checkRetentionTerm,
  checkSequence,
  checkFormedAt,
  checkHeader,
  checkTransferDue,
]

/**
 * Run the whole rule pack against one filing register.
 * @param input - normalized register.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value and rule selection.
 * @returns the report, with `skipped` listing every check that did not run.
 */
export function runCheck(input: ArchiveInput, ruleset: Ruleset, options: CheckOptions): Report {
  const disabled = new Set([...ruleset.disabled, ...options.disabledRules])
  const only = new Set(options.onlyRules)
  const base = {
    input,
    ruleset,
    issues: [] as Issue[],
    skipped: [] as Skipped[],
    fired: new Set<string>(),
    skipReasons: new Map<string, string>(),
    options,
  }
  const context: RuleContext = {
    ...base,
    add: makeAdd(base),
    skip: (ruleId, reason) => {
      base.skipReasons.set(ruleId, reason)
    },
  }

  for (const checker of CHECKERS) checker(context)

  const withNote = (reason: string): string => (options.skipNotes === undefined ? reason : `${reason}；${options.skipNotes}`)
  const skipped: Skipped[] = disabledAsSkipped(ruleset, [...disabled], withNote('该规则在当前配置中被禁用'))
  const already = new Set(skipped.map((entry) => entry.rule))
  for (const [ruleId, reason] of base.skipReasons) {
    if (already.has(ruleId)) continue
    if (disabled.has(ruleId) || (options.onlyRules.length > 0 && !only.has(ruleId))) continue
    skipped.push({ rule: ruleId, reason: withNote(reason) })
    already.add(ruleId)
  }
  for (const rule of ruleset.rules) {
    if (disabled.has(rule.id) || base.fired.has(rule.id) || already.has(rule.id)) continue
    if (options.onlyRules.length > 0 && !only.has(rule.id)) continue
    skipped.push({ rule: rule.id, reason: withNote('材料满足该检查的前置条件且未发现差异条目') })
  }
  if (options.onlyRules.length > 0) {
    const notSelected = ruleset.rules.filter((rule) => !only.has(rule.id) && !disabled.has(rule.id))
    if (notSelected.length > 0) {
      skipped.push({
        rule: notSelected.map((rule) => rule.id).join(','),
        reason: withNote(`本次调用通过 only 参数把执行范围限制为 ${[...only].join(', ')}，上列规则未执行`),
      })
    }
  }

  return makeReport({
    plugin: options.plugin,
    target: input.target,
    rulesetVersion: ruleset.version,
    checkedAt: options.checkedAt,
    issues: context.issues,
    skipped,
  })
}
