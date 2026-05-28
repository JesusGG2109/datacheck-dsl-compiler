import { useEffect, useMemo, useRef, useState, type CSSProperties, type DragEvent, type ReactNode } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import * as Tabs from '@radix-ui/react-tabs'
import {
  Activity,
  AlertTriangle,
  BookOpen,
  Braces,
  Check,
  Command,
  Copy,
  FileCode2,
  FileUp,
  Info,
  Layers3,
  Play,
  Rows3,
  ScrollText,
  Terminal,
  UploadCloud,
} from 'lucide-react'

import { Button } from './components/ui/button'
import { Card } from './components/ui/card'
import {
  analyzeDataCheck,
  type AnalysisResult,
  type CsvRow,
  type FieldDeclaration,
  type Rule,
  type SymbolEntry,
  type Token,
} from './lib/datacheck'

type ApiState = 'idle' | 'loading' | 'success' | 'error'
type ViewId = 'editor' | 'docs' | 'manual' | 'traces' | 'about'

const DEFAULT_DSL = `CAMPO edad NUMERICO
CAMPO nombre TEXTO
CAMPO nivel NUMERICO
CAMPO sueldo NUMERICO

REGLA edad > 18
REGLA nombre != ""
REGLA sueldo >= 1200`

const particles = Array.from({ length: 52 }, (_, index) => ({
  left: (index * 37 + 11) % 100,
  top: (index * 53 + 17) % 100,
  delay: (index % 13) * 0.27,
  duration: 8 + (index % 7),
  opacity: 0.16 + (index % 4) * 0.05,
}))

function App() {
  const [started, setStarted] = useState(false)
  const [source, setSource] = useState(DEFAULT_DSL)
  const [csvSource, setCsvSource] = useState('')
  const [csvName, setCsvName] = useState('sin CSV cargado')
  const [runCount, setRunCount] = useState(0)
  const [analysis, setAnalysis] = useState<AnalysisResult>(() => clearedAnalysisState())
  const [apiState, setApiState] = useState<ApiState>('idle')
  const [connectionError, setConnectionError] = useState('')
  const [currentView, setCurrentView] = useState<ViewId>('editor')

  const logs = useMemo(() => {
    if (apiState !== 'success') {
      return []
    }
    return [`RUN ${String(runCount).padStart(2, '0')} :: DataCheck compiler pipeline`].concat(analysis.logs)
  }, [analysis.logs, apiState, runCount])

  useEffect(() => {
    if (!started) {
      return
    }

    const controller = new AbortController()
    const delay = runCount === 0 ? 0 : 450
    const clearTimeout = window.setTimeout(() => {
      if (controller.signal.aborted) {
        return
      }
      setApiState('loading')
      setConnectionError('')
      setAnalysis(clearedAnalysisState())
    }, 0)

    const timeout = window.setTimeout(async () => {
      try {
        const nextAnalysis = await analyzeDataCheck(source, csvSource, controller.signal)
        setAnalysis(nextAnalysis)
        setApiState('success')
      } catch (error) {
        if (controller.signal.aborted) {
          return
        }
        const message = error instanceof Error ? error.message : 'error desconocido'
        setAnalysis(clearedAnalysisState())
        setApiState('error')
        setConnectionError(message)
      }
    }, delay)

    return () => {
      controller.abort()
      window.clearTimeout(clearTimeout)
      window.clearTimeout(timeout)
    }
  }, [csvSource, runCount, source, started])

  const handleCsv = (file: File) => {
    const reader = new FileReader()
    reader.onload = () => {
      setCsvSource(String(reader.result ?? ''))
      setCsvName(file.name)
    }
    reader.readAsText(file)
  }

  return (
    <main className="studio-root">
      <Atmosphere />
      <AnimatePresence mode="wait">
        {!started ? (
          <Hero key="hero" onStart={() => setStarted(true)} />
        ) : (
          <Studio
            key="studio"
            currentView={currentView}
            onViewChange={setCurrentView}
            source={source}
            onSourceChange={setSource}
            csvName={csvName}
            onCsvFile={handleCsv}
            analysis={analysis}
            rows={analysis.csvResult}
            totalRows={analysis.csvTotalRows}
            headers={analysis.csvHeaders}
            logs={logs}
            apiState={apiState}
            connectionError={connectionError}
            onRun={() => setRunCount((value) => value + 1)}
          />
        )}
      </AnimatePresence>
    </main>
  )
}

function Atmosphere() {
  return (
    <div className="atmosphere" aria-hidden="true">
      <motion.div
        className="aurora-surface"
        animate={{ backgroundPosition: ['0% 42%', '100% 58%', '0% 42%'] }}
        transition={{ duration: 24, repeat: Infinity, ease: 'easeInOut' }}
      />
      <div className="particle-field">
        {particles.map((particle, index) => (
          <span
            key={index}
            className="particle"
            style={
              {
                left: `${particle.left}%`,
                top: `${particle.top}%`,
                opacity: particle.opacity,
                '--delay': `${particle.delay}s`,
                '--duration': `${particle.duration}s`,
              } as CSSProperties
            }
          />
        ))}
      </div>
    </div>
  )
}

function Hero({ onStart }: { onStart: () => void }) {
  return (
    <motion.section
      className="hero-screen"
      initial={{ opacity: 0, filter: 'blur(18px)' }}
      animate={{ opacity: 1, filter: 'blur(0px)' }}
      exit={{ opacity: 0, filter: 'blur(16px)', scale: 0.98 }}
      transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
    >
      <motion.div
        className="hero-console"
        initial={{ opacity: 0, y: 28 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.12, duration: 0.72, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="hero-chip">
          <Command size={15} />
          DataCheck Studio
        </div>
        <h1>DataCheck Studio</h1>
        <p>Data filtering powered by formal languages</p>
        <div className="hero-actions">
          <Button variant="primary" size="lg" onClick={onStart}>
            <Play size={18} />
            Iniciar análisis
          </Button>
        </div>
      </motion.div>
    </motion.section>
  )
}

type StudioProps = {
  currentView: ViewId
  onViewChange: (view: ViewId) => void
  source: string
  onSourceChange: (value: string) => void
  csvName: string
  onCsvFile: (file: File) => void
  analysis: AnalysisResult
  rows: CsvRow[]
  totalRows: number
  headers: string[]
  logs: string[]
  apiState: ApiState
  connectionError: string
  onRun: () => void
}

function Studio({
  currentView,
  onViewChange,
  source,
  onSourceChange,
  csvName,
  onCsvFile,
  analysis,
  rows,
  totalRows,
  headers,
  logs,
  apiState,
  connectionError,
  onRun,
}: StudioProps) {
  return (
    <motion.section
      className="studio-shell"
      initial={{ opacity: 0, y: 24, filter: 'blur(14px)' }}
      animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
      transition={{ duration: 0.72, ease: [0.16, 1, 0.3, 1] }}
    >
      <Sidebar currentView={currentView} onViewChange={onViewChange} />
      <section className="studio-workspace">
        <TopBar
          csvName={csvName}
          onCsvFile={onCsvFile}
          onRun={onRun}
          tokenCount={analysis.tokens.length}
          errorCount={analysis.errors.length}
          rowCount={rows.length}
          totalRows={totalRows}
          apiState={apiState}
        />
        <ConnectionBanner apiState={apiState} message={connectionError} />

        {currentView === 'editor' ? (
          <>
            <div className="workbench-grid">
              <EditorPanel source={source} onChange={onSourceChange} tokens={analysis.tokens} />
              <RightPanel analysis={analysis} rows={rows} headers={headers} apiState={apiState} connectionError={connectionError} />
            </div>
            <Console logs={logs} />
          </>
        ) : currentView === 'docs' ? (
          <DocumentationView />
        ) : currentView === 'manual' ? (
          <ManualView />
        ) : currentView === 'traces' ? (
          <TracesView logs={logs} apiState={apiState} />
        ) : (
          <AboutView />
        )}
      </section>
    </motion.section>
  )
}

const SIDEBAR_ITEMS: { view: ViewId; icon: typeof FileCode2; label: string }[] = [
  { view: 'editor', icon: FileCode2, label: 'Editor' },
  { view: 'docs', icon: BookOpen, label: 'Documentación' },
  { view: 'manual', icon: ScrollText, label: 'Manual' },
  { view: 'traces', icon: Terminal, label: 'Trazas' },
  { view: 'about', icon: Info, label: 'Acerca de' },
]

function Sidebar({ currentView, onViewChange }: { currentView: ViewId; onViewChange: (v: ViewId) => void }) {
  return (
    <aside className="icon-rail">
      <div className="rail-logo">
        <Command size={20} />
      </div>
      <nav className="rail-nav" aria-label="Navegación DataCheck Studio">
        {SIDEBAR_ITEMS.map(({ view, icon: Icon, label }) => (
          <button
            key={view}
            type="button"
            className={`rail-button ${currentView === view ? 'rail-button-active' : ''}`}
            data-tooltip={label}
            aria-label={label}
            aria-current={currentView === view ? 'page' : undefined}
            onClick={() => onViewChange(view)}
          >
            <Icon size={19} strokeWidth={1.85} />
            {currentView === view ? <span className="rail-active" /> : null}
          </button>
        ))}
      </nav>
    </aside>
  )
}

type TopBarProps = {
  csvName: string
  onCsvFile: (file: File) => void
  onRun: () => void
  tokenCount: number
  errorCount: number
  rowCount: number
  totalRows: number
  apiState: ApiState
}

function TopBar({ csvName, onCsvFile, onRun, tokenCount, errorCount, rowCount, totalRows, apiState }: TopBarProps) {
  return (
    <Card className="topbar">
      <div className="brand-block">
        <div className="brand-mark">
          <Layers3 size={18} />
        </div>
        <div>
          <strong>DataCheck Studio</strong>
          <span>DSL compiler workspace</span>
        </div>
      </div>

      <div className="status-strip">
        <Metric icon={<Braces size={15} />} label="Tokens" value={tokenCount} tone="emerald" />
        <Metric icon={<AlertTriangle size={15} />} label="Errores" value={errorCount} tone={errorCount ? 'red' : 'blue'} />
        <Metric icon={<Rows3 size={15} />} label="Filas" value={`${rowCount}/${totalRows}`} tone="blue" />
      </div>

      <CsvDropzone csvName={csvName} onCsvFile={onCsvFile} compact />

      <Button variant="primary" onClick={onRun} disabled={apiState === 'loading'}>
        <Play size={16} />
        {apiState === 'loading' ? 'Analizando' : 'Analizar'}
      </Button>
    </Card>
  )
}

function ConnectionBanner({ apiState, message }: { apiState: ApiState; message: string }) {
  const content = {
    idle: {
      title: 'Sin análisis ejecutado',
      detail: 'La interfaz espera una respuesta real de FastAPI.',
    },
    loading: {
      title: 'Analizando con Python',
      detail: 'Lexer, parser, semántica y CSV se están ejecutando en FastAPI.',
    },
    success: {
      title: 'FastAPI conectado',
      detail: 'Los paneles muestran datos reales del compilador Python.',
    },
    error: {
      title: 'Backend desconectado',
      detail: message || 'No se pudo conectar con FastAPI.',
    },
  }[apiState]

  return (
    <Card className={`connection-banner connection-banner-${apiState}`}>
      <span className="connection-pulse" />
      <strong>{content.title}</strong>
      <em>{content.detail}</em>
    </Card>
  )
}

function Metric({
  icon,
  label,
  value,
  tone,
}: {
  icon: ReactNode
  label: string
  value: number | string
  tone: 'emerald' | 'blue' | 'red'
}) {
  return (
    <div className={`metric metric-${tone}`}>
      {icon}
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

function CsvDropzone({
  csvName,
  onCsvFile,
  compact = false,
}: {
  csvName: string
  onCsvFile: (file: File) => void
  compact?: boolean
}) {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [dragging, setDragging] = useState(false)

  const acceptFile = (file?: File) => {
    if (file) {
      onCsvFile(file)
    }
  }

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setDragging(false)
    acceptFile(event.dataTransfer.files[0])
  }

  return (
    <div
      className={`csv-dropzone ${compact ? 'csv-dropzone-compact' : ''} ${dragging ? 'is-dragging' : ''}`}
      onClick={() => inputRef.current?.click()}
      onDragOver={(event) => {
        event.preventDefault()
        setDragging(true)
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      role="button"
      tabIndex={0}
    >
      <input
        ref={inputRef}
        className="sr-only"
        type="file"
        accept=".csv,text/csv"
        onChange={(event) => acceptFile(event.target.files?.[0])}
      />
      <UploadCloud size={compact ? 16 : 22} />
      <div>
        <strong>{compact ? 'CSV' : 'Upload CSV'}</strong>
        <span>{csvName}</span>
      </div>
    </div>
  )
}

function EditorPanel({ source, onChange, tokens }: { source: string; onChange: (value: string) => void; tokens: Token[] }) {
  return (
    <Card className="editor-panel">
      <div className="panel-header">
        <div>
          <span className="panel-kicker">DSL</span>
          <h2>Compiler Editor</h2>
        </div>
        <div className="editor-status">
          <span className="live-dot" />
          lexical AFD
        </div>
      </div>
      <CodeEditor source={source} onChange={onChange} tokens={tokens} />
    </Card>
  )
}

function CodeEditor({ source, onChange, tokens }: { source: string; onChange: (value: string) => void; tokens: Token[] }) {
  const [scrollTop, setScrollTop] = useState(0)
  const lines = useMemo(() => toLines(source), [source])
  const tokenMap = useMemo(() => {
    const map = new Map<number, Token[]>()
    for (const token of tokens) {
      const lineTokens = map.get(token.line) ?? []
      lineTokens.push(token)
      map.set(token.line, lineTokens)
    }
    return map
  }, [tokens])

  return (
    <div className="code-editor">
      <div className="code-gutter" aria-hidden="true">
        <div style={{ transform: `translateY(-${scrollTop}px)` }}>
          {lines.map((_, index) => (
            <div className="line-number" key={index}>
              {index + 1}
            </div>
          ))}
        </div>
      </div>
      <div className="code-pane">
        <pre className="highlight-layer" aria-hidden="true">
          <code style={{ transform: `translateY(-${scrollTop}px)` }}>
            {lines.map((line, index) => (
              <span className="highlight-line" key={`${index}-${line}`}>
                {renderHighlightedLine(line, index + 1, tokenMap.get(index + 1) ?? [])}
              </span>
            ))}
          </code>
        </pre>
        <textarea
          className="dsl-textarea"
          value={source}
          spellCheck={false}
          onChange={(event) => onChange(event.target.value)}
          onScroll={(event) => setScrollTop(event.currentTarget.scrollTop)}
          aria-label="Editor DataCheck DSL"
        />
        <motion.span
          className="editor-caret-glow"
          animate={{ opacity: [0.25, 1, 0.25] }}
          transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>
    </div>
  )
}

function renderHighlightedLine(line: string, lineNumber: number, lineTokens: Token[]) {
  const pieces: ReactNode[] = []
  let cursor = 1

  for (const token of lineTokens) {
    if (token.column > cursor) {
      pieces.push(<span key={`${lineNumber}-${cursor}-plain`}>{line.slice(cursor - 1, token.column - 1)}</span>)
    }
    pieces.push(
      <span className={syntaxClass(token)} key={token.id}>
        {token.lexeme}
      </span>,
    )
    cursor = token.column + token.lexeme.length
  }

  if (cursor <= line.length) {
    pieces.push(<span key={`${lineNumber}-tail`}>{line.slice(cursor - 1)}</span>)
  }

  if (pieces.length === 0) {
    return <span>&nbsp;</span>
  }
  return pieces
}

function syntaxClass(token: Token) {
  if (token.token.startsWith('TOKEN_')) {
    return 'syntax-keyword'
  }
  if (token.token === 'IDENTIFICADOR') {
    return 'syntax-identifier'
  }
  if (token.token === 'NUMERO') {
    return 'syntax-number'
  }
  if (token.token === 'CADENA') {
    return 'syntax-string'
  }
  if (token.token === 'OPERADOR_RELACIONAL') {
    return 'syntax-operator'
  }
  return ''
}

function RightPanel({
  analysis,
  rows,
  headers,
  apiState,
  connectionError,
}: {
  analysis: AnalysisResult
  rows: CsvRow[]
  headers: string[]
  apiState: ApiState
  connectionError: string
}) {
  return (
    <Card className="right-panel">
      <Tabs.Root defaultValue="tokens" className="tabs-root">
        <Tabs.List className="tabs-list" aria-label="Panel inteligente">
          <Tabs.Trigger value="tokens">Tokens</Tabs.Trigger>
          <Tabs.Trigger value="errors">Errores</Tabs.Trigger>
          <Tabs.Trigger value="symbols">Símbolos</Tabs.Trigger>
          <Tabs.Trigger value="analysis">Análisis</Tabs.Trigger>
          <Tabs.Trigger value="csv">CSV</Tabs.Trigger>
        </Tabs.List>

        <Tabs.Content value="tokens" className="tab-content">
          <TokenList tokens={analysis.tokens} />
        </Tabs.Content>
        <Tabs.Content value="errors" className="tab-content">
          <ErrorList analysis={analysis} apiState={apiState} connectionError={connectionError} />
        </Tabs.Content>
        <Tabs.Content value="symbols" className="tab-content">
          <SymbolTable symbols={analysis.symbols} />
        </Tabs.Content>
        <Tabs.Content value="analysis" className="tab-content">
          <AnalysisPanel declarations={analysis.declarations} rules={analysis.rules} />
        </Tabs.Content>
        <Tabs.Content value="csv" className="tab-content">
          <ResultTable rows={rows} headers={headers} />
        </Tabs.Content>
      </Tabs.Root>
    </Card>
  )
}

const PHASE_LABELS: Record<string, string> = {
  lexico: 'LEX',
  sintactico: 'SIN',
  semantico: 'SEM',
}

function symTypeClass(semanticType: string): string {
  if (semanticType === 'TEXTO') return 'sym-type-texto'
  if (semanticType === 'NO_DECLARADO') return 'sym-type-none'
  return ''
}

function symCatClass(category: string): string {
  if (category === 'CAMPO+REGLA') return 'sym-cat-both'
  if (category === 'CAMPO') return 'sym-cat-campo'
  if (category === 'REGLA') return 'sym-cat-regla'
  return 'sym-cat-none'
}

function TokenList({ tokens }: { tokens: Token[] }) {
  return (
    <div className="token-list">
      {tokens.map((token) => (
        <motion.div
          className="token-row"
          key={token.id}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.22 }}
        >
          <span>{token.lexeme}</span>
          <strong>{token.token}</strong>
          <em>
            {token.line}:{token.column}
          </em>
        </motion.div>
      ))}
    </div>
  )
}

function ErrorList({
  analysis,
  apiState,
  connectionError,
}: {
  analysis: AnalysisResult
  apiState: ApiState
  connectionError: string
}) {
  if (apiState === 'error') {
    return (
      <div className="empty-state empty-state-error">
        <AlertTriangle size={24} />
        <strong>Backend desconectado</strong>
        <span>{connectionError || 'No se pudo conectar con FastAPI'}</span>
      </div>
    )
  }

  if (apiState === 'loading') {
    return (
      <div className="empty-state">
        <Activity size={24} />
        <strong>Analizando</strong>
        <span>Esperando respuesta del compilador Python</span>
      </div>
    )
  }

  if (analysis.errors.length === 0) {
    return (
      <div className="empty-state">
        <Activity size={24} />
        <strong>Sin errores</strong>
        <span>AFD aceptados</span>
      </div>
    )
  }

  return (
    <div className="error-list">
      {analysis.errors.map((error) => (
        <div className="error-row" key={`${error.code}-${error.line}-${error.column}-${error.description}`}>
          <AlertTriangle size={16} />
          <div>
            <div className="error-row-meta">
              <span className={`error-phase-badge error-phase-${error.phase}`}>
                {PHASE_LABELS[error.phase] ?? error.phase}
              </span>
              <strong>#{error.code}</strong>
            </div>
            <span>{error.description}</span>
          </div>
          <em>
            {error.line}:{error.column}
          </em>
        </div>
      ))}
    </div>
  )
}

function SymbolTable({ symbols }: { symbols: SymbolEntry[] }) {
  if (symbols.length === 0) {
    return (
      <div className="empty-state">
        <Braces size={24} />
        <strong>Sin identificadores</strong>
        <span>Declara campos con CAMPO para poblar la tabla</span>
      </div>
    )
  }
  return (
    <div className="symbol-table">
      <div className="symbol-head">
        <span>Identificador</span>
        <span>Tipo sem.</span>
        <span>Categoría</span>
        <span>Lín.</span>
      </div>
      {symbols.map((sym) => (
        <div className="symbol-row" key={sym.id}>
          <span>{sym.lexeme}</span>
          <span className={`sym-type-badge ${symTypeClass(sym.semanticType)}`}>
            {sym.semanticType}
          </span>
          <span className={`sym-cat-badge ${symCatClass(sym.category)}`}>
            {sym.category}
          </span>
          <em>{sym.line}</em>
        </div>
      ))}
    </div>
  )
}

function AnalysisPanel({
  declarations,
  rules,
}: {
  declarations: FieldDeclaration[]
  rules: Rule[]
}) {
  return (
    <div className="analysis-panel">
      <div className="analysis-section">
        <div className="analysis-section-title">
          <Layers3 size={12} />
          Declaraciones de campos ({declarations.length})
        </div>
        {declarations.length === 0 ? (
          <div className="empty-state" style={{ minHeight: 80 }}>
            <span>Sin declaraciones CAMPO</span>
          </div>
        ) : (
          <>
            <div className="decl-head">
              <span>Campo</span>
              <span>Tipo</span>
              <span>Lín.</span>
            </div>
            {declarations.map((decl) => (
              <div className="decl-row" key={`decl-${decl.name}-${decl.line}`}>
                <span className="decl-name">{decl.name}</span>
                <span className={`decl-type-badge ${decl.type === 'TEXTO' ? 'decl-type-texto' : ''}`}>
                  {decl.type}
                </span>
                <em>{decl.line}</em>
              </div>
            ))}
          </>
        )}
      </div>

      <div className="analysis-section">
        <div className="analysis-section-title">
          <Activity size={12} />
          Reglas de filtro ({rules.length})
        </div>
        {rules.length === 0 ? (
          <div className="empty-state" style={{ minHeight: 80 }}>
            <span>Sin reglas REGLA</span>
          </div>
        ) : (
          <>
            <div className="rule-head">
              <span>Campo</span>
              <span>Op.</span>
              <span>Valor</span>
              <span>Tipo</span>
              <span>Lín.</span>
            </div>
            {rules.map((rule, i) => (
              <div className="rule-row" key={`rule-${rule.field}-${rule.line}-${i}`}>
                <span className="decl-name">{rule.field}</span>
                <span className="rule-op-badge">{rule.operator}</span>
                <span className="decl-name">{String(rule.value ?? '')}</span>
                <span className={`decl-type-badge ${rule.valueType === 'TEXTO' ? 'decl-type-texto' : ''}`}>
                  {rule.valueType}
                </span>
                <em>{rule.line}</em>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  )
}

function ResultTable({ rows, headers }: { rows: CsvRow[]; headers: string[] }) {
  if (headers.length === 0) {
    return (
      <div className="empty-state">
        <FileUp size={24} />
        <strong>CSV vacío</strong>
        <span>Dataset pendiente</span>
      </div>
    )
  }

  return (
    <div className="result-table-wrap">
      <table className="result-table">
        <thead>
          <tr>
            {headers.map((header) => (
              <th key={header}>{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <motion.tr
              key={`${rowIndex}-${headers[0] ? row[headers[0]] : rowIndex}`}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.22, delay: rowIndex * 0.025 }}
            >
              {headers.map((header) => (
                <td key={`${rowIndex}-${header}`}>{row[header]}</td>
              ))}
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function Console({ logs }: { logs: string[] }) {
  const visibleLogs = logs.slice(Math.max(0, logs.length - 88))

  return (
    <Card className="console-panel">
      <div className="console-header">
        <div>
          <Terminal size={16} />
          Consola
        </div>
        <span>formal trace</span>
      </div>
      <div className="console-lines">
        {visibleLogs.map((line, index) => (
          <p key={`${index}-${line}`}>
            <span>$</span>
            {line}
          </p>
        ))}
      </div>
    </Card>
  )
}

function clearedAnalysisState(): AnalysisResult {
  return {
    tokens: [],
    errors: [],
    lexicalErrors: [],
    syntaxErrors: [],
    semanticErrors: [],
    symbols: [],
    declarations: [],
    rules: [],
    logs: [],
    csvResult: [],
    csvHeaders: [],
    csvTotalRows: 0,
  }
}

// ─── Documentation views ──────────────────────────────────────────────────────

function DocSection({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="doc-section">
      <h3 className="doc-section-title">{title}</h3>
      {children}
    </section>
  )
}

function DocCode({ children }: { children: string }) {
  return <pre className="doc-code"><code>{children}</code></pre>
}

function CopyExample({ label, code }: { label: string; code: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(code).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1800)
    })
  }

  return (
    <div className="copy-example">
      <div className="copy-example-header">
        <span className="copy-example-label">{label}</span>
        <button type="button" className="copy-btn" onClick={handleCopy} aria-label="Copiar código">
          {copied ? <Check size={14} /> : <Copy size={14} />}
          {copied ? 'Copiado' : 'Copiar'}
        </button>
      </div>
      <pre className="doc-code"><code>{code}</code></pre>
    </div>
  )
}

function DocumentationView() {
  return (
    <div className="doc-view">
      <div className="doc-view-header">
        <BookOpen size={20} />
        <h2>Documentación Técnica</h2>
        <span>DataCheck DSL — Lenguajes y Autómatas II</span>
      </div>

      <div className="doc-body">
        <DocSection title="Gramática formal">
          <DocCode>{`PROGRAMA      → SENTENCIA*
SENTENCIA     → DECLARACION | REGLA
DECLARACION   → CAMPO IDENTIFICADOR TIPO
TIPO          → NUMERICO | TEXTO
REGLA         → REGLA IDENTIFICADOR OPERADOR_RELACIONAL VALOR
VALOR         → NUMERO | CADENA`}</DocCode>
        </DocSection>

        <DocSection title="Pipeline del compilador">
          <div className="doc-pipeline">
            {[
              { step: '1', phase: 'Léxico', desc: 'AFDs para palabras reservadas (Trie-DFA), identificadores, números, cadenas y operadores. Genera stream de tokens.' },
              { step: '2', phase: 'Sintáctico', desc: 'Parser descendente recursivo con lookahead. Valida estructura CAMPO/REGLA. Recuperación por línea con _sincronizar().' },
              { step: '3', phase: 'Semántico', desc: 'Verifica tipos, detecta campos no declarados, valida coherencia tipo-operador y columnas CSV presentes.' },
              { step: '4', phase: 'Filtrado CSV', desc: 'Aplica las reglas compiladas sobre el dataset. Retorna filas que satisfacen todas las condiciones.' },
            ].map(({ step, phase, desc }) => (
              <div className="doc-pipeline-step" key={step}>
                <span className="doc-step-num">{step}</span>
                <div>
                  <strong>{phase}</strong>
                  <span>{desc}</span>
                </div>
              </div>
            ))}
          </div>
        </DocSection>

        <DocSection title="Tipos de tokens">
          <div className="doc-table">
            <div className="doc-table-head"><span>Token</span><span>Descripción</span><span>Ejemplo</span></div>
            {[
              ['TOKEN_CAMPO', 'Palabra reservada', 'CAMPO'],
              ['TOKEN_REGLA', 'Palabra reservada', 'REGLA'],
              ['TOKEN_NUMERICO', 'Tipo numérico', 'NUMERICO'],
              ['TOKEN_TEXTO', 'Tipo texto', 'TEXTO'],
              ['IDENTIFICADOR', 'Nombre de campo', 'edad, nombre, sueldo'],
              ['OPERADOR_RELACIONAL', 'Operador de comparación', '>, <, >=, <=, ==, !='],
              ['NUMERO', 'Literal numérico', '18, 1200, 3.14'],
              ['CADENA', 'Literal de texto', '"activo", ""'],
            ].map(([token, desc, example]) => (
              <div className="doc-table-row" key={token}>
                <code>{token}</code><span>{desc}</span><em>{example}</em>
              </div>
            ))}
          </div>
        </DocSection>

        <DocSection title="Códigos de error">
          <div className="doc-table">
            <div className="doc-table-head"><span>Código</span><span>Fase</span><span>Descripción</span></div>
            {[
              ['100', 'Léxico', 'Carácter no reconocido por ningún AFD'],
              ['101', 'Léxico', 'Cadena sin cerrar (EOF dentro de comillas)'],
              ['102', 'Léxico', 'Número con formato inválido'],
              ['103', 'Léxico', 'Operador incompleto o no reconocido'],
              ['201', 'Sintáctico', 'Declaración CAMPO incompleta o mal formada'],
              ['202', 'Sintáctico', 'Regla REGLA incompleta o mal formada'],
              ['301', 'Semántico', 'Campo no declarado usado en REGLA'],
              ['302', 'Semántico', 'Tipo de operando incompatible con el tipo del campo'],
              ['303', 'Semántico', 'Operador relacional inválido para el tipo dado'],
              ['304', 'Semántico', 'Columna CSV ausente para campo declarado'],
            ].map(([code, phase, desc]) => (
              <div className="doc-table-row" key={code}>
                <code className="doc-error-code">#{code}</code><span className={`doc-phase-tag doc-phase-${phase.toLowerCase().slice(0,3)}`}>{phase}</span><span>{desc}</span>
              </div>
            ))}
          </div>
        </DocSection>

        <DocSection title="Autómatas (AFDs)">
          <p className="doc-paragraph">
            El analizador léxico implementa autómatas finitos deterministas para cada categoría de token.
            Las palabras reservadas (<code>CAMPO</code>, <code>REGLA</code>, <code>NUMERICO</code>, <code>TEXTO</code>) se
            reconocen mediante un Trie-DFA que comparte prefijos. Los identificadores siguen el patrón
            <code> [a-zA-Z_][a-zA-Z0-9_]*</code>. Los números aceptan enteros y decimales. Las cadenas
            delimitan con comillas dobles y aceptan cualquier carácter interior excepto salto de línea.
          </p>
        </DocSection>
      </div>
    </div>
  )
}

const MANUAL_EXAMPLES = [
  {
    label: 'Filtro numérico básico',
    code: `CAMPO edad NUMERICO
CAMPO sueldo NUMERICO

REGLA edad > 18
REGLA sueldo >= 1200`,
  },
  {
    label: 'Filtro de texto con desigualdad',
    code: `CAMPO nombre TEXTO
CAMPO estado TEXTO

REGLA nombre != ""
REGLA estado == "activo"`,
  },
  {
    label: 'Múltiples campos y reglas mixtas',
    code: `CAMPO edad NUMERICO
CAMPO nombre TEXTO
CAMPO nivel NUMERICO
CAMPO sueldo NUMERICO

REGLA edad > 18
REGLA nombre != ""
REGLA nivel >= 2
REGLA sueldo >= 1200`,
  },
  {
    label: 'Error léxico: carácter inválido',
    code: `CAMPO edad NUMERICO
CAMPO nombre@ TEXTO

REGLA edad > 18`,
  },
]

function ManualView() {
  return (
    <div className="doc-view">
      <div className="doc-view-header">
        <ScrollText size={20} />
        <h2>Manual de Usuario</h2>
        <span>Guía práctica del DSL DataCheck</span>
      </div>

      <div className="doc-body">
        <DocSection title="Sintaxis DSL">
          <p className="doc-paragraph">
            DataCheck define un lenguaje de dominio específico de dos tipos de sentencias.
            Cada sentencia debe escribirse en una sola línea. El orden recomendado es declarar
            todos los <code>CAMPO</code> primero y luego las <code>REGLA</code>.
          </p>
          <div className="doc-syntax-block">
            <div className="doc-syntax-rule">
              <span className="doc-syntax-tag">DECLARACIÓN</span>
              <DocCode>{`CAMPO <identificador> <NUMERICO | TEXTO>`}</DocCode>
            </div>
            <div className="doc-syntax-rule">
              <span className="doc-syntax-tag">REGLA</span>
              <DocCode>{`REGLA <identificador> <operador> <valor>`}</DocCode>
            </div>
          </div>
          <div className="doc-table" style={{ marginTop: 10 }}>
            <div className="doc-table-head"><span>Operador</span><span>Semántica</span><span>Tipos válidos</span></div>
            {[
              ['>', 'Mayor que', 'NUMERICO'],
              ['<', 'Menor que', 'NUMERICO'],
              ['>=', 'Mayor o igual', 'NUMERICO'],
              ['<=', 'Menor o igual', 'NUMERICO'],
              ['==', 'Igual a', 'NUMERICO / TEXTO'],
              ['!=', 'Distinto de', 'NUMERICO / TEXTO'],
            ].map(([op, sem, types]) => (
              <div className="doc-table-row" key={op}>
                <code>{op}</code><span>{sem}</span><em>{types}</em>
              </div>
            ))}
          </div>
        </DocSection>

        <DocSection title="Ejemplos listos para usar">
          <p className="doc-paragraph">
            Copia cualquier ejemplo al editor con el botón <strong>Copiar</strong>, carga un CSV
            compatible y pulsa <strong>Analizar</strong>.
          </p>
          <div className="copy-example-list">
            {MANUAL_EXAMPLES.map((ex) => (
              <CopyExample key={ex.label} label={ex.label} code={ex.code} />
            ))}
          </div>
        </DocSection>

        <DocSection title="Flujo de trabajo recomendado">
          <ol className="doc-ol">
            <li>Escribe las declaraciones <code>CAMPO</code> para todos los campos del CSV.</li>
            <li>Añade las reglas <code>REGLA</code> con los filtros deseados.</li>
            <li>Carga el archivo CSV usando el botón de la barra superior.</li>
            <li>Pulsa <strong>Analizar</strong> para ejecutar el compilador.</li>
            <li>Revisa la pestaña <strong>Errores</strong> si hay problemas de sintaxis o semántica.</li>
            <li>Consulta la pestaña <strong>CSV</strong> para ver las filas filtradas.</li>
          </ol>
        </DocSection>
      </div>
    </div>
  )
}

function TracesView({ logs, apiState }: { logs: string[]; apiState: ApiState }) {
  const lexerLines = logs.filter((l) => l.startsWith('[LEXER]'))
  const parserLines = logs.filter((l) => l.startsWith('[PARSER'))
  const semanticLines = logs.filter((l) => l.startsWith('[SEMANTIC]') || l.startsWith('[SEM]'))
  const otherLines = logs.filter(
    (l) => !l.startsWith('[LEXER]') && !l.startsWith('[PARSER') && !l.startsWith('[SEMANTIC]') && !l.startsWith('[SEM]'),
  )

  return (
    <div className="doc-view">
      <div className="doc-view-header">
        <Terminal size={20} />
        <h2>Trazas del Compilador</h2>
        <span>Salida formal del pipeline de análisis</span>
      </div>

      {apiState === 'idle' && (
        <div className="empty-state" style={{ marginTop: 48 }}>
          <Activity size={28} />
          <strong>Sin traza disponible</strong>
          <span>Ejecuta un análisis desde el editor para ver la traza completa</span>
        </div>
      )}

      {apiState === 'loading' && (
        <div className="empty-state" style={{ marginTop: 48 }}>
          <Activity size={28} />
          <strong>Compilando…</strong>
          <span>Esperando respuesta del backend</span>
        </div>
      )}

      {apiState === 'error' && (
        <div className="empty-state empty-state-error" style={{ marginTop: 48 }}>
          <AlertTriangle size={28} />
          <strong>Backend desconectado</strong>
          <span>No hay traza disponible sin conexión con FastAPI</span>
        </div>
      )}

      {apiState === 'success' && logs.length === 0 && (
        <div className="empty-state" style={{ marginTop: 48 }}>
          <Activity size={28} />
          <strong>Traza vacía</strong>
          <span>No se generaron entradas de traza en el último análisis</span>
        </div>
      )}

      {apiState === 'success' && logs.length > 0 && (
        <div className="doc-body">
          {lexerLines.length > 0 && (
            <DocSection title={`Léxico (${lexerLines.length} entradas)`}>
              <div className="trace-block">
                {lexerLines.map((line, i) => <p key={i} className="trace-line trace-lexico">{line}</p>)}
              </div>
            </DocSection>
          )}
          {parserLines.length > 0 && (
            <DocSection title={`Sintáctico (${parserLines.length} entradas)`}>
              <div className="trace-block">
                {parserLines.map((line, i) => (
                  <p key={i} className={`trace-line ${line.includes('ERROR') ? 'trace-error' : line.includes('SYNC') ? 'trace-sync' : 'trace-parser'}`}>{line}</p>
                ))}
              </div>
            </DocSection>
          )}
          {semanticLines.length > 0 && (
            <DocSection title={`Semántico (${semanticLines.length} entradas)`}>
              <div className="trace-block">
                {semanticLines.map((line, i) => <p key={i} className="trace-line trace-semantic">{line}</p>)}
              </div>
            </DocSection>
          )}
          {otherLines.length > 0 && (
            <DocSection title={`General (${otherLines.length} entradas)`}>
              <div className="trace-block">
                {otherLines.map((line, i) => <p key={i} className="trace-line">{line}</p>)}
              </div>
            </DocSection>
          )}
        </div>
      )}
    </div>
  )
}

function AboutView() {
  return (
    <div className="doc-view">
      <div className="doc-view-header">
        <Info size={20} />
        <h2>Acerca del Proyecto</h2>
        <span>DataCheck Studio — Compilador académico DSL</span>
      </div>

      <div className="doc-body">
        <DocSection title="Información del proyecto">
          <div className="about-grid">
            {[
              ['Proyecto', 'DataCheck Studio'],
              ['Autor', 'Jesús Grangeno García'],
              ['Institución', 'Tecnológico Nacional de México (TECNM)'],
              ['Materia', 'Lenguajes y Autómatas II'],
              ['Propósito', 'Compilador académico para DSL de validación y filtrado de datasets CSV'],
            ].map(([label, value]) => (
              <div className="about-row" key={label}>
                <span className="about-label">{label}</span>
                <span className="about-value">{value}</span>
              </div>
            ))}
          </div>
        </DocSection>

        <DocSection title="Descripción técnica">
          <p className="doc-paragraph">
            DataCheck Studio implementa un compilador completo de cuatro fases para un lenguaje
            de dominio específico orientado a la validación y filtrado de archivos CSV.
            El compilador está escrito en <strong>Python 3</strong> con <strong>FastAPI</strong> como
            servidor REST, e integra un frontend en <strong>React 19 + TypeScript</strong> con
            diseño futurista oscuro.
          </p>
          <p className="doc-paragraph">
            Cada fase (léxica, sintáctica, semántica y de filtrado) produce resultados
            independientes accesibles a través de la API. Los errores están clasificados por
            fase y código, con recuperación sintáctica por sincronización de línea para
            minimizar errores en cascada.
          </p>
        </DocSection>

        <DocSection title="Tecnologías">
          <div className="doc-table">
            <div className="doc-table-head"><span>Capa</span><span>Tecnología</span></div>
            {[
              ['Backend — Compilador', 'Python 3, autómatas AFD, parser recursivo descendente'],
              ['Backend — API', 'FastAPI, Pydantic, Uvicorn'],
              ['Frontend — UI', 'React 19, TypeScript, Vite'],
              ['Frontend — Estilos', 'Tailwind CSS v4, Framer Motion, Radix UI'],
              ['Iconografía', 'Lucide React'],
            ].map(([layer, tech]) => (
              <div className="doc-table-row" key={layer}>
                <span>{layer}</span><span>{tech}</span>
              </div>
            ))}
          </div>
        </DocSection>

        <DocSection title="Características del compilador">
          <ul className="doc-ul">
            <li>Analizador léxico con AFDs formales (Trie-DFA para palabras reservadas)</li>
            <li>Parser descendente recursivo con lookahead y recuperación de errores por línea</li>
            <li>Análisis semántico de tipos, operadores y coherencia con columnas CSV</li>
            <li>Tabla de símbolos enriquecida con tipo semántico y categoría por identificador</li>
            <li>Filtrado real de datasets CSV con las reglas compiladas</li>
            <li>Trazabilidad completa del pipeline en consola formal</li>
            <li>Clasificación de errores en tres fases: léxico, sintáctico, semántico</li>
          </ul>
        </DocSection>
      </div>
    </div>
  )
}

// ─── Utilities ────────────────────────────────────────────────────────────────

function toLines(source: string) {
  const lines = ['']
  for (let index = 0; index < source.length; index += 1) {
    const char = source[index]
    if (char === '\r') {
      continue
    }
    if (char === '\n') {
      lines.push('')
    } else {
      lines[lines.length - 1] += char
    }
  }
  return lines
}

export default App
