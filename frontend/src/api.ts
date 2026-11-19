/** Large integers are always decimal strings; never convert witnesses to JS Number. */
export type AlgorithmName = 'Fermat' | 'Solovay-Strassen' | 'Miller-Rabin'
export type Verdict = 'verified_prime' | 'probably_prime' | 'composite'

export interface RoundLog {
  round_idx: number
  witness_a: string
  expression: string
  computed_value: string
  passed: boolean
  note: string
}
export interface AlgorithmResult {
  algorithm: AlgorithmName
  verdict: 'Prime' | 'Probably Prime' | 'Composite'
  is_prime: boolean
  rounds_requested: number
  rounds_run: number
  elapsed_ms: number
  error_bound: string
  pre_filtered: boolean
  logs: RoundLog[]
}
export interface CheckResponse {
  n: string
  bit_length: number
  digit_length: number
  k: number
  verdict: Verdict
  explanation: string
  algorithms: AlgorithmResult[]
}
export interface TraceStep {
  title: string
  formula: string
  value: string
  explanation: string
  status: 'pass' | 'fail' | 'info'
}
export interface TraceResponse {
  steps: TraceStep[]
  matches_log: boolean
  computed_pass: boolean
  truncated: boolean
}
export interface CarmichaelResponse {
  n: string
  is_carmichael: boolean | null
  fermat_fooled: boolean
  factorization_complete: boolean
  factors: number[]
  factor_powers: [number, number][]
  korselt_details: string[]
  algorithms: AlgorithmResult[]
}
export interface BenchmarkRow {
  Bit_Length: number
  Candidate_Type: string
  Algorithm: AlgorithmName
  Trials: number
  Rounds: number
  Avg_Time_ms: number
  Median_Time_ms: number
  Std_Dev_ms: number
  Min_Time_ms: number
  Max_Time_ms: number
  Verdict: string
  Error_Bound: string
  Verdict_Consistency: string
  Avg_Rounds_Run: number
  Min_Rounds_Run: number
  Max_Rounds_Run: number
}
export interface BenchmarkResponse {
  rows: BenchmarkRow[]
  config: { bit_sizes: number[]; k: number; trials: number }
}

const BASE = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

async function request<T>(path: string, body?: unknown, signal?: AbortSignal): Promise<T> {
  let response: Response
  try {
    response = await fetch(BASE + path, {
      method: body === undefined ? 'GET' : 'POST',
      headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal,
    })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') throw error
    throw new Error('Python API bilan aloqa yo‘q. Backend serverini ishga tushiring (8000-port).')
  }
  const payload: unknown = await response.json().catch(() => null)
  if (!response.ok) {
    const detail = payload && typeof payload === 'object' && 'detail' in payload
      ? (payload as { detail: unknown }).detail
      : null
    throw new Error(typeof detail === 'string' ? detail : 'Server so‘rovni bajara olmadi.')
  }
  return payload as T
}

export const api = {
  check: (n: string, k: number) => request<CheckResponse>('/api/check', { n, k }),
  trace: (n: string, algorithm: AlgorithmName, log: RoundLog, signal?: AbortSignal) =>
    request<TraceResponse>('/api/trace', { n, algorithm, log }, signal),
  carmichael: (n: string, k: number) =>
    request<CarmichaelResponse>('/api/carmichael', { n, k }),
  benchmark: (bit_sizes: number[], k: number, trials: number) =>
    request<BenchmarkResponse>('/api/benchmark', { bit_sizes, k, trials }),
}

export function formatTime(ms: number) {
  return ms < 0.0001 ? '< 0.0001 ms' : ms.toFixed(4) + ' ms'
}

export function smallNumber(value: string, edge = 19) {
  return value.length <= edge * 2 + 4
    ? value
    : value.slice(0, edge) + '…' + value.slice(-edge)
}

export function validateIntegerString(value: string): string | null {
  const clean = value.replace(/[\s_]/g, '')
  if (!/^[0-9]+$/.test(clean)) return 'Faqat natural sonning raqamlarini kiriting.'
  if (clean.length > 2048) return 'Son uzunligi 2048 raqamdan oshmasin.'
  if (BigInt(clean) < 2n) return 'Son kamida 2 bo‘lishi kerak.'
  return null
}
