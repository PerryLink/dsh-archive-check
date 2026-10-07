/**
 * Input contract for the archive filing checker.
 *
 * The material is one归档 register: a list of file items with the descriptive
 * fields a register carries, plus an optional retention-period table. The checker
 * verifies that each item is described completely enough to be filed and found
 * again, and that the retention arithmetic is consistent — it never decides
 * whether a particular document *should* have been archived, which is the
 * archivist's judgement.
 */

/** One row of the filing register. */
export interface ArchiveItem {
  /** 1-based row number in the source. */
  row: number
  /** Values keyed by the source's own column names. */
  fields: Record<string, string>
  /** 档号, when the register carries one. */
  reference?: string
  /** 题名. */
  title?: string
  /** 保管期限 as written, e.g. `永久` or `定期30年`. */
  retention?: string
  /** 形成日期 as written. */
  formedAt?: string
  /** 件号 or 序号. */
  sequence?: string
}

/** The whole normalized input. */
export interface ArchiveInput {
  target: string
  /** 全宗名称 or 立卷单位, when declared. */
  fonds?: string
  /** 年度 the register covers, when declared. */
  year?: number
  items: ArchiveItem[]
  /** Column names the reader saw, in order. */
  columns: string[]
  warnings: string[]
}

/** Column names recognised as each field, in priority order. */
export const COLUMNS = {
  reference: ['档号', '档案号', 'reference'],
  title: ['题名', '文件题名', '标题', 'title'],
  retention: ['保管期限', '期限', 'retention'],
  formedAt: ['形成日期', '日期', '成文日期', 'formedAt', 'date'],
  sequence: ['件号', '序号', 'sequence'],
} as const

/**
 * Parse a retention-period string into a classification and a year count.
 *
 * Accepts the two shapes a Chinese register uses: `永久` for permanent, and a
 * `定期N年` / `N年` form for a fixed term. Anything else returns undefined so the
 * rule can report the value it could not read rather than guessing.
 *
 * @param raw - the register's own wording.
 * @returns `{ permanent: true }`, `{ permanent: false, years }`, or undefined.
 */
export function parseRetention(raw: string | undefined): { permanent: boolean; years?: number } | undefined {
  if (raw === undefined) return undefined
  const text = raw.replace(/[\uff10-\uff19]/g, (char) => String.fromCharCode(char.charCodeAt(0) - 0xfee0)).trim()
  if (text === '') return undefined
  if (/^(永久|长期|永)$/.test(text)) return { permanent: true }
  // Match the year count anywhere in the string, so `定期30年`, `30年`, `定期 30 年`
  // and a bare `30` all read the same way.
  const years = /(\d{1,3})\s*年?/.exec(text)
  if (years === null) return undefined
  const parsed = Number.parseInt(years[1] as string, 10)
  if (!Number.isFinite(parsed) || parsed <= 0 || parsed > 200) return undefined
  return { permanent: false, years: parsed }
}
