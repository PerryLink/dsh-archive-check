/**
 * Reader for the archive filing register.
 *
 * The register is JSON or YAML with an `items` list, each item a mapping of the
 * register's own columns. Known column names are recognised in the reader; the
 * columns it actually saw are kept so a finding can name the right one.
 */

import { YamlSubsetError, parseYaml } from './shared/yaml.ts'
import { COLUMNS } from './model.ts'
import type { ArchiveInput, ArchiveItem } from './model.ts'

/** Raised when the material cannot be read at all. */
export class MaterialError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'MaterialError'
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function text(value: unknown): string | undefined {
  if (value === undefined || value === null) return undefined
  if (typeof value === 'string') return value.trim() === '' ? undefined : value.trim()
  if (typeof value === 'number' && Number.isFinite(value)) return String(value)
  return undefined
}

/** Find the first present value among a set of candidate column names. */
function pick(fields: Record<string, string>, names: readonly string[]): string | undefined {
  for (const name of names) {
    const value = fields[name]
    if (value !== undefined && value !== '') return value
  }
  return undefined
}

function parseItem(raw: unknown, index: number): ArchiveItem {
  if (typeof raw === 'string') {
    const value = text(raw)
    if (value === undefined) throw new MaterialError(`items[${index}] 为空`)
    return { row: index + 1, fields: { 题名: value }, title: value }
  }
  if (!isRecord(raw)) throw new MaterialError(`items[${index}] 必须是映射或字符串`)
  const fields: Record<string, string> = {}
  for (const [key, value] of Object.entries(raw)) {
    if (value === undefined || value === null) continue
    const rendered = typeof value === 'string' ? value.trim() : text(value)
    fields[key] = rendered ?? ''
  }
  const item: ArchiveItem = { row: index + 1, fields }
  const reference = pick(fields, COLUMNS.reference)
  if (reference !== undefined) item.reference = reference
  const title = pick(fields, COLUMNS.title)
  if (title !== undefined) item.title = title
  const retention = pick(fields, COLUMNS.retention)
  if (retention !== undefined) item.retention = retention
  const formedAt = pick(fields, COLUMNS.formedAt)
  if (formedAt !== undefined) item.formedAt = formedAt
  const sequence = pick(fields, COLUMNS.sequence)
  if (sequence !== undefined) item.sequence = sequence
  return item
}

/**
 * Parse material into the normalized input contract.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized input.
 */
export function parseMaterial(source: string, target: string): ArchiveInput {
  const trimmed = source.trim()
  if (trimmed === '') throw new MaterialError('材料为空')
  let document: unknown
  if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
    try {
      document = JSON.parse(trimmed)
    } catch (error) {
      throw new MaterialError(`JSON 无法解析：${error instanceof Error ? error.message : String(error)}`)
    }
  } else {
    try {
      document = parseYaml(trimmed)
    } catch (error) {
      if (error instanceof YamlSubsetError) throw new MaterialError(`YAML 无法解析：${error.message}`)
      throw error
    }
  }

  const warnings: string[] = []
  let list: unknown
  let fonds: string | undefined
  let year: number | undefined
  if (Array.isArray(document)) {
    list = document
  } else if (isRecord(document)) {
    list = document.items ?? document.rows ?? document.档案
    fonds = text(document.fonds ?? document.全宗名称 ?? document.立卷单位)
    const rawYear = text(document.year ?? document.年度)
    if (rawYear !== undefined && /^\d{4}$/.test(rawYear)) year = Number.parseInt(rawYear, 10)
  } else {
    throw new MaterialError('材料根节点必须是映射或列表')
  }

  if (list === undefined || list === null) throw new MaterialError('材料缺少 items 列表，无法执行检查')
  if (!Array.isArray(list)) throw new MaterialError('items 必须是列表')
  if (list.length === 0) throw new MaterialError('items 为空列表，无法执行检查')

  const items = list.map((entry, index) => parseItem(entry, index))
  const columns = [...new Set(items.flatMap((item) => Object.keys(item.fields)))]
  const recognised = [...COLUMNS.reference, ...COLUMNS.title, ...COLUMNS.retention].some((name) => columns.includes(name))
  if (!recognised) {
    throw new MaterialError(
      `材料中没有可识别的档案字段，已识别的列名为：${columns.join(' / ') || '（无）'}；` +
        `请至少提供以下之一：${[...COLUMNS.reference, ...COLUMNS.title, ...COLUMNS.retention].join(' / ')}`,
    )
  }

  const input: ArchiveInput = { target, items, columns, warnings }
  if (fonds !== undefined) input.fonds = fonds
  if (year !== undefined) input.year = year
  if (year === undefined) warnings.push('材料未声明年度（year），按年度核对的检查将无法执行')
  return input
}
