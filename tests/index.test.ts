import { readFile, readdir } from 'node:fs/promises'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import { loadRuleset } from '../src/shared/ruleset.ts'
import { parseMaterial } from '../src/parse.ts'
import { runCheck } from '../src/check.ts'
import { buildView } from '../src/view.ts'
import { findForbiddenWording } from '../src/shared/wording.ts'
import { addDays, diffDays, parseWallClock } from '../src/shared/datetime.ts'
import { parseYaml } from '../src/shared/yaml.ts'
import { parseRetention } from '../src/model.ts'
import { Config as ConfigSchema } from '../src/config.ts'
import { inject, name as pluginName, resolvePackageFile, TOOL_NAME } from '../src/index.ts'
import type { Report } from '../src/shared/report.ts'
import type { CheckOptions } from '../src/check.ts'

const here = dirname(fileURLToPath(import.meta.url))
const packageRoot = resolve(here, '..')
const rulesPath = join(packageRoot, 'rules', 'archive-check.yaml')
const fixturesRoot = join(here, 'fixtures')
const CHECKED_AT = '2026-10-06T00:00:00.000Z'

interface CaseFile {
  ruleId: string
  configure?: Record<string, Record<string, unknown>>
  pairs: { name: string; material: string; expect: { ruleId: string; count: number } }[]
}

async function loadPack() {
  return loadRuleset(await readFile(rulesPath, 'utf8'))
}

function runOptions(overrides: Partial<CheckOptions> = {}): CheckOptions {
  return { plugin: pluginName, checkedAt: CHECKED_AT, disabledRules: [], onlyRules: [], ...overrides }
}

function withConfiguration(ruleset: Awaited<ReturnType<typeof loadPack>>, configure: CaseFile['configure']) {
  if (configure === undefined) return ruleset
  return {
    ...ruleset,
    rules: ruleset.rules.map((rule) =>
      configure[rule.id] === undefined ? rule : { ...rule, params: { ...rule.params, ...configure[rule.id] } },
    ),
  }
}

async function runFixture(materialText: string, target: string, configure?: CaseFile['configure']): Promise<Report> {
  const ruleset = withConfiguration(await loadPack(), configure)
  // The retention vocabulary is a deployment setting, so the fixture drives it the
  // same way a real configuration would.
  const terms = configure?.['AR-003']?.retentionTerms
  return runCheck(
    parseMaterial(materialText, target),
    ruleset,
    runOptions(Array.isArray(terms) ? { retentionTerms: terms as string[] } : {}),
  )
}

function issuesOf(report: Report, ruleId: string) {
  return report.issues.filter((issue) => issue.ruleId === ruleId)
}

async function ruleDirectories(): Promise<string[]> {
  const entries = await readdir(fixturesRoot, { withFileTypes: true })
  return entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name).sort()
}

async function readCases(directory: string): Promise<CaseFile> {
  return JSON.parse(await readFile(join(fixturesRoot, directory, 'cases.json'), 'utf8')) as CaseFile
}

const GOOD = {
  fonds: '某单位',
  year: 2026,
  items: [
    { 档号: 'A-2026-001', 题名: '关于第一项工作的通知', 保管期限: '永久', 形成日期: '2026-03-15', 件号: '1' },
    { 档号: 'A-2026-002', 题名: '关于第二项工作的通知', 保管期限: '定期30年', 形成日期: '2026-04-01', 件号: '2' },
  ],
}

describe('rule pack', () => {
  it('declares a citable basis for every rule', async () => {
    const ruleset = await loadPack()
    expect(ruleset.plugin).toBe(pluginName)
    expect(ruleset.rules.length).toBeGreaterThanOrEqual(6)
    for (const rule of ruleset.rules) {
      expect(rule.basis.document, `${rule.id} document`).not.toBe('')
      expect(rule.basis.clause, `${rule.id} clause`).not.toBe('')
      expect(rule.basis.excerpt.length, `${rule.id} excerpt`).toBeGreaterThanOrEqual(8)
      expect(rule.basis.source, `${rule.id} source`).toMatch(/^https?:\/\//)
      expect(['direct', 'derived-from-principle', 'institutional-configuration']).toContain(rule.basis.kind)
    }
  })

  it('never lets a principle-derived or locally configured check be an error', async () => {
    const ruleset = await loadPack()
    for (const rule of ruleset.rules) {
      if (rule.basis.kind === 'derived-from-principle') expect(rule.severity, rule.id).not.toBe('error')
      if (rule.basis.kind === 'institutional-configuration') expect(rule.severity, rule.id).toBe('info')
    }
  })

  it('cites only the verified sources, and never the outdated point of the retention rule', async () => {
    const ruleset = await loadPack()
    for (const rule of ruleset.rules) {
      expect(rule.basis.excerpt, rule.id).not.toContain('本次未取得')
      expect(rule.basis.clause, rule.id).not.toBe('第一条')
      for (const extra of rule.alsoBasis ?? []) {
        expect(extra.clause, rule.id).not.toBe('第一条')
      }
    }
    const numbers = ruleset.rules.flatMap((rule) => [rule.basis.number, ...(rule.alsoBasis ?? []).map((extra) => extra.number)])
    expect(numbers.some((number) => number.includes('国务院令第772号'))).toBe(true)
    expect(numbers.some((number) => number.includes('国家档案局令第8号'))).toBe(true)
    expect(numbers.some((number) => number.includes('国家档案局令第10号'))).toBe(true)
    expect(numbers.some((number) => number.includes('DA/T 22'))).toBe(true)
  })

  it('attributes the transfer years to the regulation, never to the law', async () => {
    const ruleset = await loadPack()
    const transfer = ruleset.rules.find((rule) => rule.id === 'AR-007')
    expect(transfer?.basis.number).toContain('国务院令第772号')
    expect(transfer?.basis.clause).toBe('第二十条第二款')
    expect(transfer?.basis.excerpt).toContain('满二十年')
    const lawBasis = transfer?.alsoBasis?.find((extra) => extra.document.includes('档案法'))
    expect(lawBasis?.clause).toBe('第十五条')
    // The law's article 15 has no year figure; the pack must say so.
    expect(lawBasis?.excerpt).not.toContain('二十年')
    expect(transfer?.note).toContain('不含任何年限')
  })

  it('never claims a national retention table exists', async () => {
    const source = await readFile(rulesPath, 'utf8')
    expect(source).toContain('不存在全国通用、可直接适用的唯一保管期限表')
    expect(source).toContain('最低期限')
    // A retention period above the national figure is lawful for enterprises.
    const ruleset = await loadPack()
    expect(ruleset.rules.find((rule) => rule.id === 'AR-003')?.note).toContain('这不是错误')
  })

  it('ships both local vocabularies empty', async () => {
    const ruleset = await loadPack()
    expect(ruleset.rules.find((rule) => rule.id === 'AR-001')?.params.requiredFields).toEqual([])
    expect(ruleset.rules.find((rule) => rule.id === 'AR-003')?.params.retentionTerms).toEqual([])
  })

  it('refuses a rule pack that overstates a principle-derived check', () => {
    const overstated = [
      'plugin: probe',
      'version: "0"',
      'rules:',
      '  - id: X-001',
      '    title: probe',
      '    severity: error',
      '    basis:',
      '      document: 《X》',
      '      number: X〔2020〕1号',
      '      clause: 第一条',
      '      excerpt: 这是一个足够长的逐字摘录示例。',
      '      kind: derived-from-principle',
      '      source: https://example.invalid/x',
    ].join('\n')
    expect(() => loadRuleset(overstated)).toThrow(/strongest permitted severity/)
  })
})

describe('paired fixtures', () => {
  it('has both a compliant and a violating sample for every rule', async () => {
    const ruleset = await loadPack()
    const covered = new Set<string>()
    for (const directory of await ruleDirectories()) {
      const cases = await readCases(directory)
      expect(cases.pairs.filter((pair) => pair.expect.count === 0).length, `${directory} compliant sample`).toBeGreaterThanOrEqual(1)
      expect(cases.pairs.filter((pair) => pair.expect.count > 0).length, `${directory} violating sample`).toBeGreaterThanOrEqual(1)
      for (const pair of cases.pairs) {
        const material = await readFile(join(fixturesRoot, directory, pair.material), 'utf8')
        const report = await runFixture(material, pair.material, cases.configure)
        const matched = issuesOf(report, cases.ruleId)
        expect(
          matched.length,
          `${directory}/${pair.name} expected ${pair.expect.count} × ${cases.ruleId}, got ${matched.map((issue) => issue.found).join(' | ')}`,
        ).toBe(pair.expect.count)
        covered.add(cases.ruleId)
      }
    }
    for (const rule of ruleset.rules) expect(covered.has(rule.id), `covered ${rule.id}`).toBe(true)
  })

  it('gives every issue a citable basis and a stable id', async () => {
    for (const directory of await ruleDirectories()) {
      const cases = await readCases(directory)
      for (const pair of cases.pairs) {
        const material = await readFile(join(fixturesRoot, directory, pair.material), 'utf8')
        const report = await runFixture(material, pair.material, cases.configure)
        for (const issue of report.issues) {
          expect(issue.basis).toContain('「')
          expect(issue.id).toMatch(/^dsh-archive-check\.AR-\d{3}\.[0-9a-f]{8}$/)
          expect(issue.found).not.toBe('')
          expect(issue.expected).not.toBe('')
        }
      }
    }
  })
})

describe('retention vocabulary', () => {
  it('reads the two shapes a register uses', () => {
    expect(parseRetention('永久')).toEqual({ permanent: true })
    expect(parseRetention('长期')).toEqual({ permanent: true })
    expect(parseRetention('定期30年')).toEqual({ permanent: false, years: 30 })
    expect(parseRetention('１０年')).toEqual({ permanent: false, years: 10 })
    expect(parseRetention('五年')).toBeUndefined()
    expect(parseRetention('')).toBeUndefined()
    expect(parseRetention(undefined)).toBeUndefined()
  })

  it('reports a term it cannot read separately from a term outside the list', async () => {
    const ruleset = withConfiguration(await loadPack(), { 'AR-003': { retentionTerms: ['永久', '定期30年'] } })
    const material = JSON.stringify({
      fonds: '某单位',
      year: 2026,
      items: [
        { 档号: 'A-1', 题名: '甲', 保管期限: '五年' },
        { 档号: 'A-2', 题名: '乙', 保管期限: '定期20年' },
      ],
    })
    const report = runCheck(parseMaterial(material, 'inline'), ruleset, runOptions({ retentionTerms: ['永久', '定期30年'] }))
    const found = issuesOf(report, 'AR-003')
    expect(found).toHaveLength(2)
    expect(found[0]?.found).toContain('不是可识别的期限用词')
    expect(found[1]?.found).toContain('不在本机构配置的期限用词内')
  })

  it('ignores whitespace when deciding whether a reference repeats', async () => {
    const ruleset = await loadPack()
    const material = JSON.stringify({
      fonds: '某单位',
      year: 2026,
      items: [
        { 档号: 'A-2026-001', 题名: '甲' },
        { 档号: 'A-2026- 001', 题名: '乙' },
      ],
    })
    const report = runCheck(parseMaterial(material, 'inline'), ruleset, runOptions())
    expect(issuesOf(report, 'AR-002')).toHaveLength(1)
  })

  it('leaves alphanumeric 件号 out of the continuity check', async () => {
    const ruleset = await loadPack()
    const material = JSON.stringify({
      fonds: '某单位',
      year: 2026,
      items: [
        { 档号: 'A-1', 题名: '甲', 件号: 'A-1' },
        { 档号: 'A-2', 题名: '乙', 件号: 'A-3' },
      ],
    })
    const report = runCheck(parseMaterial(material, 'inline'), ruleset, runOptions())
    expect(issuesOf(report, 'AR-004')).toHaveLength(0)
    expect(report.skipped.find((entry) => entry.rule === 'AR-004')?.reason).toContain('少于 2 个')
  })
})

describe('skipped reporting', () => {
  it('admits that the descriptive list is not configured', async () => {
    const report = await runFixture(JSON.stringify(GOOD), 'inline')
    expect(report.skipped.find((entry) => entry.rule === 'AR-001')?.reason).toContain('未配置 requiredFields')
  })

  it('admits that the retention vocabulary is not configured', async () => {
    const report = await runFixture(JSON.stringify(GOOD), 'inline')
    expect(report.skipped.find((entry) => entry.rule === 'AR-003')?.reason).toContain('retentionTerms')
  })

  it('warns when the register declares no year', () => {
    const input = parseMaterial(JSON.stringify({ items: [{ 档号: 'A-1', 题名: '甲' }] }), 'inline')
    expect(input.warnings.join(' ')).toContain('未声明年度')
  })

  it('names disabled rules exactly once and appends the configured note', async () => {
    const ruleset = await loadPack()
    const input = parseMaterial(JSON.stringify(GOOD), 'inline')
    const report = runCheck(input, ruleset, runOptions({ disabledRules: ['AR-006'], skipNotes: '本机构档案细则' }))
    const entries = report.skipped.filter((item) => item.rule === 'AR-006')
    expect(entries).toHaveLength(1)
    expect(entries[0]?.reason).toContain('禁用')
    expect(entries[0]?.reason).toContain('本机构档案细则')
  })
})

describe('report rendering', () => {
  it('never uses adjudicating wording and always carries the disclaimer', async () => {
    const material = await readFile(join(fixturesRoot, 'AR-002', 'AR-002-unsafe.json'), 'utf8')
    const report = await runFixture(material, 'AR-002-unsafe.json')
    const view = buildView(report)
    expect(findForbiddenWording(view.markdown)).toEqual([])
    expect(view.markdown).toContain('免责声明')
    expect(view.markdown).toContain('未执行的检查')
    expect(JSON.parse(view.reportJson)).toMatchObject({ plugin: pluginName, summary: report.summary })
  })
})

describe('plugin contract', () => {
  it('declares a static inject array covering every service apply touches', () => {
    expect(Array.isArray(inject)).toBe(true)
    expect(inject).toContain('tools')
  })

  it('exposes a Schemastery Config with serializable defaults', () => {
    const resolved = ConfigSchema(null)
    expect(resolved.rulesFile).toBe('rules/archive-check.yaml')
    expect(resolved.disabledRules).toEqual([])
    expect(resolved.timeoutMs).toBeGreaterThan(0)
  })

  it('resolves the packaged rule pack and rejects a missing one', () => {
    expect(resolvePackageFile('rules/archive-check.yaml')).toBe(rulesPath)
    expect(() => resolvePackageFile('rules/does-not-exist.yaml')).toThrow(/未找到/)
  })

  it('names the tool after the package family convention', () => {
    expect(TOOL_NAME).toBe('archive_check')
  })
})

describe('material reader', () => {
  it('rejects empty material instead of reporting an empty result', () => {
    expect(() => parseMaterial('   ', 'inline')).toThrow(/材料为空/)
  })

  it('rejects a register with no recognisable archive columns', () => {
    expect(() => parseMaterial(JSON.stringify({ items: [{ 备注: '甲' }] }), 'inline')).toThrow(/没有可识别的档案字段/)
  })

  it('accepts a plain list of titles', () => {
    const input = parseMaterial(JSON.stringify(['关于甲的通知', '关于乙的通知']), 'inline')
    expect(input.items[0]?.title).toBe('关于甲的通知')
  })
})

describe('shared kit', () => {
  it('parses wall-clock timestamps and rejects impossible dates', () => {
    expect(parseWallClock('2026-03-15')).toEqual({ date: '2026-03-15', time: '00:00', hasTime: false, minutes: 0 })
    expect(parseWallClock('二〇二六年三月十五日')).toBeUndefined()
  })

  it('does calendar arithmetic', () => {
    expect(addDays('2026-03-31', 1)).toBe('2026-04-01')
    expect(diffDays('2026-03-01', '2026-03-06')).toBe(5)
  })

  it('reads the supported YAML subset and rejects the rest', () => {
    expect(parseYaml('a: 1\nb:\n  - x\n')).toEqual({ a: 1, b: ['x'] })
    expect(() => parseYaml('a: 1\na: 2\n')).toThrow(/duplicate/)
  })
})
