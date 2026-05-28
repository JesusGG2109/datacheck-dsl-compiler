export type Token = {
  id: string
  lexeme: string
  token: string
  type: string
  value: string | number | null
  line: number
  column: number
}

export type SymbolEntry = {
  id: string
  lexeme: string
  token: string
  type: string
  semanticType: string
  category: string
  inRule: boolean
  line: number
  column: number
}

export type AnalysisError = {
  code: number
  description: string
  line: number
  column: number
  phase: 'lexico' | 'sintactico' | 'semantico'
}

export type FieldDeclaration = {
  name: string
  type: 'NUMERICO' | 'TEXTO'
  line: number
  column: number
}

export type Rule = {
  field: string
  operator: string
  value: string | number | null
  valueType: 'NUMERICO' | 'TEXTO'
  line: number
  column: number
}

export type CsvRow = Record<string, string>

export type AnalysisResult = {
  tokens: Token[]
  errors: AnalysisError[]
  lexicalErrors: AnalysisError[]
  syntaxErrors: AnalysisError[]
  semanticErrors: AnalysisError[]
  symbols: SymbolEntry[]
  declarations: FieldDeclaration[]
  rules: Rule[]
  logs: string[]
  csvResult: CsvRow[]
  csvHeaders: string[]
  csvTotalRows: number
}

type BackendToken = {
  lexema: string
  token: string
  tipo: string
  valor: string | number | null
  linea: number
  columna: number
}

type BackendSymbol = {
  lexema: string
  token: string
  tipo: string
  tipo_semantico: string
  categoria: string
  en_regla: boolean
  linea: number
  columna: number
}

type BackendError = {
  codigo: number
  descripcion: string
  linea: number
  columna: number
}

type BackendDeclaration = {
  nombre: string
  tipo: 'NUMERICO' | 'TEXTO'
  linea: number
  columna: number
}

type BackendRule = {
  campo: string
  operador: string
  valor: string | number | null
  tipo_valor: 'NUMERICO' | 'TEXTO'
  linea: number
  columna: number
}

type BackendAnalyzeResponse = {
  tokens: BackendToken[]
  errores_lexicos: BackendError[]
  errores_sintacticos: BackendError[]
  errores_semanticos: BackendError[]
  tabla_simbolos: BackendSymbol[]
  traza: string[]
  csv_resultado: CsvRow[]
  csv_headers: string[]
  csv_total_filas: number
  declaraciones: BackendDeclaration[]
  reglas: BackendRule[]
}

const API_BASE_URL = 'https://datacheck-api-8rld.onrender.com'

export async function analyzeDataCheck(source: string, csv: string, signal?: AbortSignal): Promise<AnalysisResult> {
  let response: Response

  try {
    response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ source, csv }),
      signal,
    })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw error
    }
    throw new Error('No se pudo conectar con FastAPI', { cause: error })
  }

  if (!response.ok) {
    throw new Error(`FastAPI respondió ${response.status}`)
  }

  const payload = (await response.json()) as BackendAnalyzeResponse
  return mapBackendAnalysis(payload)
}

export async function getTokens(source: string, csv: string, signal?: AbortSignal) {
  const result = await analyzeDataCheck(source, csv, signal)
  return result.tokens
}

export async function getErrors(source: string, csv: string, signal?: AbortSignal) {
  const result = await analyzeDataCheck(source, csv, signal)
  return result.errors
}

export async function getSymbolTable(source: string, csv: string, signal?: AbortSignal) {
  const result = await analyzeDataCheck(source, csv, signal)
  return result.symbols
}

export async function runCsvFilter(source: string, csv: string, signal?: AbortSignal) {
  const result = await analyzeDataCheck(source, csv, signal)
  return result.csvResult
}

function mapBackendAnalysis(payload: BackendAnalyzeResponse): AnalysisResult {
  const tokens = payload.tokens.map(mapToken)
  const symbols = payload.tabla_simbolos.map(mapSymbol)
  const lexicalErrors = payload.errores_lexicos.map((e) => mapError(e, 'lexico'))
  const syntaxErrors = payload.errores_sintacticos.map((e) => mapError(e, 'sintactico'))
  const semanticErrors = payload.errores_semanticos.map((e) => mapError(e, 'semantico'))

  return {
    tokens,
    errors: [...lexicalErrors, ...syntaxErrors, ...semanticErrors],
    lexicalErrors,
    syntaxErrors,
    semanticErrors,
    symbols,
    declarations: payload.declaraciones.map((d) => ({
      name: d.nombre,
      type: d.tipo,
      line: d.linea,
      column: d.columna,
    })),
    rules: payload.reglas.map((r) => ({
      field: r.campo,
      operator: r.operador,
      value: r.valor,
      valueType: r.tipo_valor,
      line: r.linea,
      column: r.columna,
    })),
    logs: payload.traza,
    csvResult: payload.csv_resultado,
    csvHeaders: payload.csv_headers,
    csvTotalRows: payload.csv_total_filas,
  }
}

function mapToken(token: BackendToken, index: number): Token {
  return {
    id: `${token.linea}:${token.columna}:${token.token}:${index}`,
    lexeme: token.lexema,
    token: token.token,
    type: token.tipo,
    value: token.valor,
    line: token.linea,
    column: token.columna,
  }
}

function mapSymbol(sym: BackendSymbol, index: number): SymbolEntry {
  return {
    id: `sym:${sym.linea}:${sym.columna}:${sym.lexema}:${index}`,
    lexeme: sym.lexema,
    token: sym.token,
    type: sym.tipo,
    semanticType: sym.tipo_semantico,
    category: sym.categoria,
    inRule: sym.en_regla,
    line: sym.linea,
    column: sym.columna,
  }
}

function mapError(error: BackendError, phase: AnalysisError['phase']): AnalysisError {
  return {
    code: error.codigo,
    description: error.descripcion,
    line: error.linea,
    column: error.columna,
    phase,
  }
}
