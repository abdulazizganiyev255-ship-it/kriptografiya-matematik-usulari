import { useEffect, useMemo, useState, type FormEvent } from 'react'
import katex from 'katex'
import {
  Activity, ArrowRight, BarChart3, BookOpen, Check, ChevronLeft, ChevronRight,
  CircleAlert, Clock3, Copy, Download, FlaskConical, Layers3, Menu, Play,
  Search, Shield, ShieldCheck, Sigma, Sparkles, X,
} from 'lucide-react'
import {
  api, formatTime, smallNumber, validateIntegerString,
  type AlgorithmName, type AlgorithmResult, type BenchmarkResponse, type BenchmarkRow,
  type CarmichaelResponse, type CheckResponse, type TraceResponse, type Verdict,
} from './api'
import {
  Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from 'recharts'

type Page = 'check' | 'compare'
type ChartStyle = 'bar' | 'line'
const PRIME_127 = '170141183460469231731687303715884105727'
const PALETTE: Record<AlgorithmName, string> = {
  Fermat: '#8875E8',
  'Solovay-Strassen': '#2CCBF2',
  'Miller-Rabin': '#D776EC',
}
const ALGO_LABEL: Record<AlgorithmName, string> = {
  Fermat: 'Fermat',
  'Solovay-Strassen': 'Solovay–Strassen',
  'Miller-Rabin': 'Miller–Rabin',
}

function statusText(verdict: Verdict): string {
  if (verdict === 'composite') return 'Aniq murakkab son'
  if (verdict === 'verified_prime') return 'Aniq tub son'
  return 'Ehtimoliy tub son'
}

function AlgorithmCard({ result }: { result: AlgorithmResult }) {
  const shownStatus = result.verdict === 'Prime'
    ? 'Aniq tub'
    : result.is_prime ? 'Ehtimoliy tub' : 'Aniq murakkab'
  const witness = result.logs.find(log => !log.passed)
  return (
    <article className={'algo-card ' + (result.is_prime ? 'algo-prime' : 'algo-composite')}>
      <div className="algo-top">
        <span className="algo-brand">
          <span className="algo-symbol" style={{ '--algorithm': PALETTE[result.algorithm] } as React.CSSProperties}>
            {result.algorithm === 'Fermat' ? 'f(x)' : result.algorithm === 'Miller-Rabin' ? 'MR' : '√'}
          </span>
          <strong>{ALGO_LABEL[result.algorithm]}</strong>
        </span>
        <span className={'status-small ' + (result.is_prime ? 'is-prime' : 'is-composite')}>
          {result.is_prime ? <Check size={14} /> : <CircleAlert size={14} />}
          {shownStatus}
        </span>
      </div>
      <dl className="result-details">
        <div><dt><Clock3 size={15} /> Bajarilish vaqti</dt><dd>{formatTime(result.elapsed_ms)}</dd></div>
        <div><dt><Activity size={15} /> Bajarilgan raundlar</dt><dd>{result.rounds_run} / {result.rounds_requested}</dd></div>
        <div><dt><Shield size={15} /> Nazariy xatolik</dt>
          <dd>{result.pre_filtered ? 'Aniq tekshiruv' : result.algorithm === 'Fermat' ? 'Universal chegara yo‘q' : result.error_bound}</dd></div>
        <div><dt><Sigma size={15} /> Murakkablik guvohi</dt>
          <dd title={witness?.witness_a}>{witness ? smallNumber(witness.witness_a, 9) : 'Topilmadi'}</dd></div>
      </dl>
    </article>
  )
}

function MathFormula({ value }: { value: string }) {
  const markup = useMemo(() => katex.renderToString(value, {
    displayMode: true, throwOnError: false, trust: false, strict: 'ignore',
  }), [value])
  return <div className="math-expression" dangerouslySetInnerHTML={{ __html: markup }} />
}

function RoundExplorer({ data }: { data: CheckResponse }) {
  const [algorithm, setAlgorithm] = useState<AlgorithmName>('Miller-Rabin')
  const [round, setRound] = useState(1)
  const [step, setStep] = useState(0)
  const [trace, setTrace] = useState<TraceResponse | null>(null)
  const [traceError, setTraceError] = useState('')
  const [showTable, setShowTable] = useState(false)
  const selected = data.algorithms.find(item => item.algorithm === algorithm)
  const record = selected?.logs.find(item => item.round_idx === round) ?? selected?.logs[0]

  useEffect(() => {
    setStep(0)
    setTrace(null)
    setTraceError('')
    if (!record) return
    const controller = new AbortController()
    api.trace(data.n, algorithm, record, controller.signal)
      .then(setTrace)
      .catch(error => {
        if (error instanceof DOMException && error.name === 'AbortError') return
        setTraceError(error instanceof Error ? error.message : 'Hisoblash xatosi')
      })
    return () => controller.abort()
  }, [data.n, algorithm, record])

  const steps = trace?.steps ?? []
  const activeStep = steps[Math.min(step, steps.length - 1)]
  const selectAlgo = (value: AlgorithmName) => {
    setAlgorithm(value)
    setRound(1)
    setStep(0)
  }
  return (
    <section className="panel trace-panel" aria-label="Matematik jarayon">
      <div className="section-header">
        <div><span className="eyebrow">MATEMATIK LABORATORIYA</span><h2>Qadam-baqadam tushuntirish</h2></div>
        <span className="section-icon"><Layers3 size={19} /></span>
      </div>
      <p className="section-note">Faqat haqiqatan bajarilgan raundlar ko‘rsatiladi. Asos qaytadan tasodifiy tanlanmaydi.</p>
      <div className="trace-toolbar">
        <label>Algoritm
          <select value={algorithm} onChange={event => selectAlgo(event.target.value as AlgorithmName)}>
            {data.algorithms.map(result => (
              <option key={result.algorithm} value={result.algorithm}>{ALGO_LABEL[result.algorithm]}</option>
            ))}
          </select>
        </label>
        {selected?.logs.length ? (
          <label>Raund
            <select value={record?.round_idx} onChange={event => { setRound(Number(event.target.value)); setStep(0) }}>
              {selected.logs.map(item => <option key={item.round_idx} value={item.round_idx}>{item.round_idx} / {selected.logs.length}</option>)}
            </select>
          </label>
        ) : <span className="muted-caption">Raund yo‘q — natija dastlabki tekshiruvda aniqlandi</span>}
      </div>
      {traceError && <div className="inline-error" role="alert">{traceError}</div>}
      {!record && <div className="empty-inline">Bu algoritmda ehtimoliy raundlar bajarilmagan.</div>}
      {record && !trace && !traceError && <div className="empty-inline">Matematik qadamlar hisoblanmoqda…</div>}
      {record && trace && activeStep && (
        <>
          <div className="trace-stage">
            <div className="trace-steps" role="list" aria-label="Hisoblash qadamlarining ro‘yxati">
              {steps.map((item, index) => (
                <button key={index} type="button" className={'trace-item ' + (index === step ? 'active ' : '') + item.status}
                  onClick={() => setStep(index)} aria-current={index === step ? 'step' : undefined}>
                  <span className="trace-dot">{index < step ? <Check size={12} /> : index + 1}</span>
                  <span>{item.title}</span>
                </button>
              ))}
            </div>
            <div className="trace-detail">
              <div className="trace-detail-top"><span>QADAM {step + 1} / {steps.length}</span>
                <span className={'step-tag ' + activeStep.status}>
                  {activeStep.status === 'pass' ? 'Sinovdan o‘tdi' : activeStep.status === 'fail' ? 'Murakkablik guvohi' : 'Hisoblash'}
                </span>
              </div>
              <h3>{activeStep.title}</h3>
              <MathFormula value={activeStep.formula} />
              <div className="computed-value" title={activeStep.value}>{activeStep.value}</div>
              <p>{activeStep.explanation}</p>
            </div>
          </div>
          <div className="trace-footer">
            <span>{step + 1}-qadam · {Math.round(((step + 1) / steps.length) * 100)}%</span>
            <div className="trace-arrows">
              <button type="button" aria-label="Oldingi qadam" onClick={() => setStep(Math.max(0, step - 1))} disabled={step === 0}><ChevronLeft size={18} /></button>
              <button type="button" aria-label="Keyingi qadam" onClick={() => setStep(Math.min(steps.length - 1, step + 1))} disabled={step === steps.length - 1}><ChevronRight size={18} /></button>
            </div>
          </div>
          <div className="step-progress"><div style={{ width: ((step + 1) / steps.length) * 100 + '%' }} /></div>
          {!trace.matches_log && <div className="inline-error" role="alert">Qayta hisoblangan natija asl jurnalga mos kelmadi. Natijaga tayanmang.</div>}
          {trace.truncated && <div className="inline-warning">Uzun ketma-ketlikning dastlabki 128 qadami ko‘rsatilgan.</div>}
          <button type="button" className="text-action" onClick={() => setShowTable(value => !value)}>
            {showTable ? 'Jadvalni yashirish' : 'Raundning barcha qadamlarini ko‘rish'} <ArrowRight size={15} />
          </button>
          {showTable && <div className="table-scroll"><table><thead><tr><th>#</th><th>Qadam</th><th>Natija</th></tr></thead>
            <tbody>{steps.map((entry, index) => <tr key={index}><td>{index + 1}</td><td>{entry.title}</td><td className="mono" title={entry.value}>{smallNumber(entry.value, 20)}</td></tr>)}</tbody>
          </table></div>}
        </>
      )}
    </section>
  )
}

function RuntimeChart({ results }: { results: AlgorithmResult[] }) {
  const chart = results.map(item => ({
    name: ALGO_LABEL[item.algorithm],
    ms: Math.max(0, item.elapsed_ms),
    color: PALETTE[item.algorithm],
  }))
  return (
    <section className="panel runtime-panel" aria-label="Bajarilish vaqti">
      <div className="section-header">
        <div><span className="eyebrow">REAL HISOBLASH</span><h2>Algoritmlar bajarilish vaqti</h2></div>
        <span className="section-icon"><BarChart3 size={19} /></span>
      </div>
      <div className="runtime-chart">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chart} margin={{ top: 22, right: 8, bottom: 8, left: -14 }}>
            <CartesianGrid stroke="#26384C" strokeDasharray="3 5" vertical={false} />
            <XAxis dataKey="name" stroke="#94A9C5" tickLine={false} axisLine={false} tick={{ fontSize: 11 }} />
            <YAxis stroke="#94A9C5" tickLine={false} axisLine={false} tick={{ fontSize: 11 }} />
            <Tooltip contentStyle={{ background: '#14243D', border: '1px solid #30445F', borderRadius: 10 }} />
            <Bar dataKey="ms" name="Vaqt (ms)" radius={[8, 8, 0, 0]} fill="#2EC7EF" maxBarSize={64} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="chart-note">Bir martalik o‘lchov. Kompyuter yuklamasiga bog‘liq; benchmark xulosasi o‘rnini bosmaydi.</p>
    </section>
  )
}

function getCSV(rows: BenchmarkRow[]) {
  if (rows.length === 0) return
  const columns = Object.keys(rows[0]) as (keyof BenchmarkRow)[]
  const encode = (value: unknown) => '"' + String(value ?? '').replace(/"/g, '""') + '"'
  const csv = [columns.join(','), ...rows.map(row => columns.map(name => encode(row[name])).join(','))].join('\r\n')
  const url = URL.createObjectURL(new Blob(['\ufeff', csv], { type: 'text/csv;charset=utf-8' }))
  const element = document.createElement('a')
  element.href = url
  element.download = 'primeguard_benchmark.csv'
  document.body.appendChild(element)
  element.click()
  element.remove()
  URL.revokeObjectURL(url)
}

function Benchmark({ rounds }: { rounds: number }) {
  const [bits, setBits] = useState<number[]>([64, 128, 256])
  const [k, setK] = useState(rounds)
  const [trials, setTrials] = useState(10)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [data, setData] = useState<BenchmarkResponse | null>(null)
  const [kind, setKind] = useState('Tub nomzod')
  const [chartStyle, setChartStyle] = useState<ChartStyle>('bar')
  const chartRows = useMemo(() => {
    const rows = data?.rows.filter(row => row.Candidate_Type === kind) ?? []
    const map = new Map<number, Record<string, string | number>>()
    rows.forEach(row => {
      const existing = map.get(row.Bit_Length) ?? { bit: String(row.Bit_Length) }
      existing[row.Algorithm] = row.Median_Time_ms
      map.set(row.Bit_Length, existing)
    })
    return Array.from(map.values())
  }, [data, kind])

  async function run() {
    if (bits.length === 0) return setError('Kamida bitta bit uzunligini tanlang.')
    setLoading(true)
    setError('')
    try { setData(await api.benchmark(bits, k, trials)) }
    catch (problem) { setError(problem instanceof Error ? problem.message : 'Benchmark xatosi') }
    finally { setLoading(false) }
  }
  const series = (Object.keys(PALETTE) as AlgorithmName[]).map(name =>
    chartStyle === 'bar'
      ? <Bar key={name} dataKey={name} name={ALGO_LABEL[name]} fill={PALETTE[name]} maxBarSize={36} radius={[5, 5, 0, 0]} />
      : <Line key={name} type="monotone" dataKey={name} name={ALGO_LABEL[name]} stroke={PALETTE[name]} strokeWidth={3} dot={{ r: 4 }} />
  )
  const graphContent = <>
    <CartesianGrid stroke="#26384C" strokeDasharray="3 5" vertical={false} />
    <XAxis dataKey="bit" stroke="#8DA4BF" tickLine={false} axisLine={false} />
    <YAxis stroke="#8DA4BF" tickLine={false} axisLine={false} />
    <Tooltip contentStyle={{ background: '#14243D', border: '1px solid #30445F', borderRadius: 10 }} />
    <Legend wrapperStyle={{ paddingTop: 14 }} />
    {series}
  </>
  return (
    <div className="workspace">
      <header className="page-heading"><span className="eyebrow">TADQIQOT · 02</span>
        <h1>Algoritmlarni taqqoslash</h1>
        <p>Bir xil nomzodlar, bir xil raundlar va takroriy o‘lchovlar yordamida samaradorlikni baholang.</p>
      </header>
      <section className="panel benchmark-controls">
        <div className="section-header"><div><span className="eyebrow">SINOV PARAMETRLARI</span><h2>Benchmark sozlamalari</h2></div><BarChart3 size={20} /></div>
        <div className="benchmark-fields">
          <fieldset><legend>Bit uzunliklari</legend><div className="bit-options">
            {[64, 128, 256, 512].map(bit => <label className={'bit-option ' + (bits.includes(bit) ? 'selected' : '')} key={bit}>
              <input type="checkbox" checked={bits.includes(bit)} onChange={() => setBits(old =>
                old.includes(bit) ? old.filter(x => x !== bit) : old.length >= 3 ? old : [...old, bit].sort((a,b) => a-b))} />
              {bit} bit
            </label>)}
          </div><small>Bir vaqtning o‘zida ko‘pi bilan 3 ta</small></fieldset>
          <label>Raundlar (k)<input type="number" min={5} max={64} value={k} onChange={event => setK(Math.max(5, Math.min(64, Number(event.target.value))))} /></label>
          <label>Takrorlashlar<input type="number" min={3} max={12} value={trials} onChange={event => setTrials(Math.max(3, Math.min(12, Number(event.target.value))))} /></label>
          <button className="button-primary" onClick={run} disabled={loading}><Play size={16} />{loading ? 'Sinov bajarilmoqda…' : 'Tezlikni tekshirish'}</button>
        </div>
        <p className="form-tip">Nomzod yaratish va dastlabki sinov vaqtga kiritilmaydi. Tavsiya: 10 takrorlash, 64–256 bit.</p>
      </section>
      {error && <div className="inline-error" role="alert">{error}</div>}
      {!data && !loading && <div className="empty-state"><BarChart3 size={36} /><h2>Natijalarni hisoblashga tayyor</h2><p>Parametrlarni tanlab, taqqoslashni boshlang. Hech qanday natija oldindan to‘qib chiqarilmaydi.</p></div>}
      {data && <>
        <section className="panel">
          <div className="section-header"><div><span className="eyebrow">MEDIAN BAJARILISH VAQTI</span><h2>Algoritmlar samaradorligi</h2></div>
            <div className="segmented"><button className={chartStyle === 'bar' ? 'active' : ''} onClick={() => setChartStyle('bar')}>Ustun</button><button className={chartStyle === 'line' ? 'active' : ''} onClick={() => setChartStyle('line')}>Chiziq</button></div></div>
          <div className="filter-pills">
            <button className={kind === 'Tub nomzod' ? 'selected' : ''} onClick={() => setKind('Tub nomzod')}>Tub nomzod</button>
            <button className={kind !== 'Tub nomzod' ? 'selected' : ''} onClick={() => setKind('Murakkab (semiprime)')}>Murakkab nomzod</button>
          </div>
          <div className="big-chart"><ResponsiveContainer width="100%" height={340}>
            {chartStyle === 'bar'
              ? <BarChart data={chartRows} margin={{ top: 16, right: 14, left: 0, bottom: 8 }}>{graphContent}</BarChart>
              : <LineChart data={chartRows} margin={{ top: 16, right: 14, left: 0, bottom: 8 }}>{graphContent}</LineChart>}
          </ResponsiveContainer></div>
          <p className="chart-note">Median vaqt (ms) · {data.config.trials} takrorlash · {data.config.k} raund · Bir xil nomzodlar</p>
        </section>
        <section className="panel results-table">
          <div className="section-header"><div><span className="eyebrow">AKADEMIK HISOBOT</span><h2>To‘liq natijalar</h2></div>
            <button className="button-outline" onClick={() => getCSV(data.rows)}><Download size={16} /> CSV yuklash</button></div>
          <div className="table-scroll"><table><thead><tr><th>Bit</th><th>Tur</th><th>Algoritm</th><th>Median</th><th>O‘rtacha</th><th>Raund</th><th>Natija</th></tr></thead><tbody>
            {data.rows.map((row, index) => <tr key={index}><td>{row.Bit_Length}</td><td>{row.Candidate_Type}</td><td>{ALGO_LABEL[row.Algorithm]}</td><td className="mono">{row.Median_Time_ms} ms</td><td className="mono">{row.Avg_Time_ms} ms</td><td>{row.Avg_Rounds_Run}</td><td>{row.Verdict_Consistency === 'Mixed' ? 'Turlicha' : row.Verdict === 'Composite' ? 'Murakkab' : 'Ehtimoliy tub'}</td></tr>)}
          </tbody></table></div>
          <p className="chart-note">CSV faylida barcha asl statistik ustunlar saqlanadi. Kuzatilgan vaqt nazariy murakkablikning isboti emas.</p>
        </section>
      </>}
    </div>
  )
}

function CarmichaelLesson({ rounds }: { rounds: number }) {
  const [open, setOpen] = useState(false)
  const [n, setN] = useState('561')
  const [data, setData] = useState<CarmichaelResponse | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  async function runLesson() {
    setBusy(true); setError(''); setData(null)
    try { setData(await api.carmichael(n, rounds)) }
    catch (problem) { setError(problem instanceof Error ? problem.message : 'Tajriba xatosi') }
    finally { setBusy(false) }
  }
  return (
    <section className="panel lesson-panel">
      <button className="lesson-toggle" onClick={() => setOpen(value => !value)} aria-expanded={open}>
        <span className="lesson-icon"><FlaskConical size={22}/></span>
        <span><strong>Karmaykl tajribasi</strong><small>Fermat testining cheklovini matematik misolda ko‘ring</small></span>
        <ChevronRight className={open ? 'rotate' : ''} size={20} />
      </button>
      {open && <div className="lesson-body">
        <p>Karmaykl sonlari murakkab bo‘lsa-da, ularga o‘zaro tub barcha asoslarda Fermat tengligi bajariladi. Shuning uchun bitta testdan o‘tish tublik isboti emas.</p>
        <div className="lesson-controls">
          <label>Namuna soni <select value={n} onChange={event => setN(event.target.value)}><option value="561">561</option><option value="1105">1105</option><option value="1729">1729</option><option value="8911">8911</option></select></label>
          <button className="button-outline" onClick={runLesson} disabled={busy}>{busy ? 'Tekshirilmoqda…' : 'Korselt mezonini tekshirish'} <ArrowRight size={15} /></button>
        </div>
        {error && <div className="inline-error" role="alert">{error}</div>}
        {data && <>
          <div className="lesson-verdict"><strong>{data.n} = {data.factors.join(' × ')}</strong><span>{data.is_carmichael ? 'Karmaykl soni — murakkab' : 'Karmaykl soni emas'}</span></div>
          <div className="lesson-grid">{data.algorithms.map(result => <div className="lesson-result" key={result.algorithm}>
            <b>{ALGO_LABEL[result.algorithm]}</b>
            <span className={result.is_prime ? 'text-amber' : 'text-green'}>{result.is_prime ? 'Sinovdan o‘tdi (isbot emas)' : 'Murakkablik aniqlandi'}</span>
          </div>)}</div>
          <div className="korselt"><b>Korselt mezoni</b>{data.korselt_details.map((line, index) => <p key={index}>• {line}</p>)}</div>
        </>}
      </div>}
    </section>
  )
}

export default function App() {
  const [page, setPage] = useState<Page>('check')
  const [mobileMenu, setMobileMenu] = useState(false)
  const [n, setN] = useState(PRIME_127)
  const [rounds, setRounds] = useState(20)
  const [result, setResult] = useState<CheckResponse | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  async function runCheck(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const validation = validateIntegerString(n)
    if (validation) return setError(validation)
    setBusy(true); setError(''); setResult(null)
    try { setResult(await api.check(n, rounds)) }
    catch (problem) { setError(problem instanceof Error ? problem.message : 'Tekshirish xatosi') }
    finally { setBusy(false) }
  }
  function preset(value: string) { setN(value); setError(''); setPage('check'); setMobileMenu(false) }
  async function copyNumber() {
    if (!result) return
    try { await navigator.clipboard.writeText(result.n); setCopied(true); window.setTimeout(() => setCopied(false), 1800) }
    catch { setCopied(false) }
  }

  const verdictIcon = result?.verdict === 'composite' ? <CircleAlert size={31} /> : <ShieldCheck size={31}/>
  return (
    <div className="app-shell">
      <aside className={'sidebar ' + (mobileMenu ? 'sidebar-open' : '')}>
        <div className="brand">
          <span className="brand-shield"><ShieldCheck size={28}/></span>
          <span><b>Prime<span>Guard</span></b><small>Tublik tekshiruvi laboratoriyasi</small></span>
          <button className="mobile-close" aria-label="Menyuni yopish" onClick={() => setMobileMenu(false)}><X size={19}/></button>
        </div>
        <div className="sidebar-divider"/>
        <div className="nav-label">ASOSIY MODULLAR</div>
        <nav aria-label="Asosiy navigatsiya" className="nav">
          <button className={'nav-button ' + (page === 'check' ? 'active' : '')} onClick={() => { setPage('check'); setMobileMenu(false) }}><Search size={19} /> Sonni tekshirish</button>
          <button className={'nav-button ' + (page === 'compare' ? 'active' : '')} onClick={() => { setPage('compare'); setMobileMenu(false) }}><BarChart3 size={19} /> Algoritmlarni taqqoslash</button>
        </nav>
        <div className="sidebar-divider"/>
        <div className="nav-label">TEZKOR MISOLLAR</div>
        <div className="preset-list">
          <button onClick={() => preset(PRIME_127)}><span>127-bit tub son</span><ChevronRight size={16}/></button>
          <button onClick={() => preset('561')}><span>Karmaykl · 561</span><ChevronRight size={16}/></button>
          <button onClick={() => preset('91')}><span>Murakkab son · 91</span><ChevronRight size={16}/></button>
          <button onClick={() => preset('17')}><span>Tub son · 17</span><ChevronRight size={16}/></button>
        </div>
        <div className="sidebar-bottom">
          <div className="mini-equation">n − 1 = 2ˢ · d <span>π</span></div>
          <span className="sidebar-status"><span/> Matematik yadro: Python</span>
          <small>Akademik loyiha · React + FastAPI</small>
        </div>
      </aside>

      {mobileMenu && <button className="sidebar-backdrop" aria-label="Menyuni yopish" onClick={() => setMobileMenu(false)}/>}
      <main className="main">
        <div className="topbar">
          <button className="menu-toggle" onClick={() => setMobileMenu(true)} aria-label="Menyuni ochish"><Menu size={22}/></button>
          <div className="breadcrumb"><span>PrimeGuard</span><ChevronRight size={14}/><strong>{page === 'check' ? 'Sonni tekshirish' : 'Taqqoslash'}</strong></div>
          <span className="version-chip"><Sparkles size={14}/> PrimeGuard 2.0</span>
        </div>

        {page === 'check' ? <div className="workspace">
          <header className="page-heading">
            <span className="eyebrow">MATEMATIK TADQIQOT · 01</span>
            <h1>Sonni tublikka tekshirish</h1>
            <p>Fermat, Solovay–Strassen va Miller–Rabin algoritmlari yordamida sonning tubligini tekshiring.</p>
          </header>
          <form className="input-panel panel" onSubmit={runCheck}>
            <div className="input-number">
              <label htmlFor="candidate">Tekshiriladigan son (n)</label>
              <input id="candidate" value={n} onChange={event => setN(event.target.value)}
                spellCheck={false} aria-describedby="number-note" />
              <small id="number-note">2 dan boshlangan, ko‘pi bilan 2048 raqamli natural son</small>
            </div>
            <div className="input-rounds">
              <label htmlFor="rounds">Raundlar (k)</label>
              <div className="stepper">
                <button type="button" aria-label="Raundni kamaytirish" onClick={() => setRounds(x => Math.max(1, x-1))}><ChevronLeft size={18}/></button>
                <input id="rounds" aria-label="Raundlar soni" type="number" min={1} max={64} value={rounds} onChange={event => setRounds(Math.max(1,Math.min(64,Number(event.target.value))))}/>
                <button type="button" aria-label="Raundni oshirish" onClick={() => setRounds(x => Math.min(64, x+1))}><ChevronRight size={18}/></button>
              </div>
            </div>
            <button type="submit" className="button-primary main-submit" disabled={busy}><Play size={18} /> {busy ? 'Tekshirilmoqda…' : 'Tekshirishni boshlash'}</button>
          </form>

          {error && <div className="inline-error" role="alert">{error}</div>}
          {!result && !busy && <div className="empty-state"><ShieldCheck size={38}/><h2>Laboratoriya tayyor</h2><p>Sonni kiriting va tekshirishni boshlang. Uch algoritmning haqiqiy hisoblangan natijalari shu yerda ko‘rsatiladi.</p></div>}
          {result && <>
            <div className="metadata-strip"><span>Bit uzunligi: <b>{result.bit_length}</b></span><span>Raqamlar: <b>{result.digit_length}</b></span><span>Raundlar: <b>{result.k}</b></span><button onClick={copyNumber} title="Sonni nusxalash"><Copy size={14}/>{copied ? 'Nusxalandi' : 'Sonni nusxalash'}</button></div>
            <section className={'verdict-banner ' + (result.verdict === 'composite' ? 'verdict-bad' : 'verdict-good')} aria-live="polite">
              <div className="verdict-symbol">{verdictIcon}</div>
              <div><span className="eyebrow">YAKUNIY XULOSA</span><h2>{statusText(result.verdict)}</h2></div>
              <p>{result.explanation}</p>
            </section>
            <div className="result-grid">{result.algorithms.map(item => <AlgorithmCard key={item.algorithm} result={item}/>)}</div>
            <div className="lower-grid"><RoundExplorer key={result.n + ':' + result.k} data={result}/><RuntimeChart results={result.algorithms}/></div>
          </>}
          <CarmichaelLesson rounds={rounds} />
          <footer className="app-footer"><BookOpen size={15}/> Probabilistik tekshiruv natijasi tublikning qat’iy isboti bo‘lmasligi mumkin.</footer>
        </div> : <Benchmark rounds={rounds}/>}
      </main>
    </div>
  )
}
