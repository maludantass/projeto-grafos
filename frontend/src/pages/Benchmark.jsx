import { useMemo, useState, useEffect } from 'react'
import reportData from '../../../out/parte2_report.json'
import styles from './Benchmark.module.css'

const COLORS = {
  'BFS': '#00e676',
  'DFS': '#d500f9',
  'Dijkstra': '#ffd700',
  'Bellman-Ford': '#ff2d78',
  'Carregamento do grafo': '#4fc3f7',
  'Componentes Conexos (DFS global)': '#ff9800',
}

function algoColor(nome) {
  for (const [k, v] of Object.entries(COLORS)) {
    if (nome.includes(k)) return v
  }
  return '#aaa'
}

function shortLabel(tarefa) {
  return tarefa
    .replace(' (Busca em Largura)', '')
    .replace(' (Busca em Profundidade)', '')
    .replace(' (caminho mínimo, single-source)', '')
    .replace(' (DFS global)', '')
}

export default function Benchmark() {
  const medicoes = reportData.medicoes
  const resumo   = reportData.resumo_comparativo
  const grafo    = reportData.grafo
  const casos    = reportData.casos_especiais_bellman_ford

  const [hoveredAlgo, setHoveredAlgo] = useState(null)
  const [sortCol,     setSortCol]     = useState('tempo_medio_ms')
  const [sortDir,     setSortDir]     = useState(-1)
  const [barsReady,   setBarsReady]   = useState(false)

  useEffect(() => {
    const t = setTimeout(() => setBarsReady(true), 80)
    return () => clearTimeout(t)
  }, [])

  const maxTempo = useMemo(
    () => Math.max(...medicoes.map(m => m.tempo_medio_ms)),
    [medicoes]
  )

  const sortedMedicoes = useMemo(() => {
    return [...medicoes].sort((a, b) => {
      const av = a[sortCol] ?? 0
      const bv = b[sortCol] ?? 0
      return sortDir * (bv - av)
    })
  }, [medicoes, sortCol, sortDir])

  function handleSort(col) {
    if (col === sortCol) setSortDir(d => -d)
    else { setSortCol(col); setSortDir(-1) }
  }

  function sortIcon(col) {
    if (col !== sortCol) return ' ↕'
    return sortDir === -1 ? ' ↓' : ' ↑'
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Painel de Benchmark</h1>
      <p className={styles.subtitle}>
        Comparação de desempenho dos algoritmos no dataset Spotify
        ({grafo.vertices.toLocaleString('pt-BR')} vértices · {grafo.arestas.toLocaleString('pt-BR')} arestas · {grafo.tipo})
      </p>

      {/* ── Gráfico de barras interativo ── */}
      <section className={styles.card}>
        <h2 className={styles.cardTitle}>Tempo médio de execução (ms)</h2>
        <div className={styles.chart}>
          {medicoes.map(m => {
            const label = shortLabel(m.tarefa)
            const pct   = barsReady ? (m.tempo_medio_ms / maxTempo) * 100 : 0
            const color = algoColor(m.tarefa)
            const isHov = hoveredAlgo === m.tarefa
            return (
              <div
                key={m.tarefa}
                className={`${styles.barRow} ${isHov ? styles.barRowHovered : ''}`}
                onMouseEnter={() => setHoveredAlgo(m.tarefa)}
                onMouseLeave={() => setHoveredAlgo(null)}
              >
                <div className={styles.barLabel} style={{ color: isHov ? '#fff' : undefined }}>
                  {label}
                </div>
                <div className={styles.barTrack}>
                  <div
                    className={styles.barFill}
                    style={{
                      width: `${pct}%`,
                      background: color,
                      boxShadow: isHov ? `0 0 16px ${color}88` : 'none',
                    }}
                  />
                  <span className={styles.barValue}>{m.tempo_medio_ms.toFixed(2)} ms</span>
                </div>
                {isHov && (
                  <div className={styles.tooltip}>
                    <div style={{ color, fontWeight: 700, marginBottom: 6 }}>● {label}</div>
                    <div>Tempo médio: <strong>{m.tempo_medio_ms.toFixed(2)} ms</strong></div>
                    <div>Tempo mínimo: <strong>{m.tempo_min_ms.toFixed(2)} ms</strong></div>
                    <div>Memória pico: <strong>{m.memoria_pico_kb.toFixed(0)} KB</strong></div>
                    <div>Complexidade: <span style={{ fontFamily: 'monospace', color: '#ffd700' }}>{m.complexidade_teorica}</span></div>
                    <div>Execuções: <strong>{m.n_runs ?? 1}</strong></div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </section>

      {/* ── Tabela com ordenação ── */}
      <section className={styles.card}>
        <h2 className={styles.cardTitle}>
          Métricas detalhadas
          <span className={styles.sortHint}>clique nos cabeçalhos para ordenar</span>
        </h2>
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Algoritmo / Tarefa</th>
                <th className={styles.sortable} onClick={() => handleSort('tempo_medio_ms')}>
                  Tempo médio (ms){sortIcon('tempo_medio_ms')}
                </th>
                <th className={styles.sortable} onClick={() => handleSort('tempo_min_ms')}>
                  Tempo mín. (ms){sortIcon('tempo_min_ms')}
                </th>
                <th className={styles.sortable} onClick={() => handleSort('memoria_pico_kb')}>
                  Memória pico (KB){sortIcon('memoria_pico_kb')}
                </th>
                <th>Complexidade</th>
                <th className={styles.sortable} onClick={() => handleSort('n_runs')}>
                  Execuções{sortIcon('n_runs')}
                </th>
              </tr>
            </thead>
            <tbody>
              {sortedMedicoes.map(m => (
                <tr
                  key={m.tarefa}
                  className={hoveredAlgo === m.tarefa ? styles.rowHovered : ''}
                  onMouseEnter={() => setHoveredAlgo(m.tarefa)}
                  onMouseLeave={() => setHoveredAlgo(null)}
                >
                  <td>
                    <span className={styles.dot} style={{ background: algoColor(m.tarefa) }} />
                    {m.tarefa}
                  </td>
                  <td className={styles.num}>{m.tempo_medio_ms.toFixed(3)}</td>
                  <td className={styles.num}>{m.tempo_min_ms.toFixed(3)}</td>
                  <td className={styles.num}>{m.memoria_pico_kb.toFixed(1)}</td>
                  <td className={styles.mono}>{m.complexidade_teorica}</td>
                  <td className={styles.num}>{m.n_runs ?? 1}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* ── Resumo comparativo ── */}
      <section className={styles.cardRow}>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>Mais rápido</div>
          <div className={styles.statVal} style={{ color: '#00e676' }}>
            {resumo.mais_rapido.algoritmo}
          </div>
          <div className={styles.statSub}>{resumo.mais_rapido.tempo_medio_ms.toFixed(2)} ms</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>Mais lento</div>
          <div className={styles.statVal} style={{ color: '#ff2d78' }}>
            {resumo.mais_lento.algoritmo}
          </div>
          <div className={styles.statSub}>{resumo.mais_lento.tempo_medio_ms.toFixed(2)} ms</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>BF mais lento que Dijkstra</div>
          <div className={styles.statVal} style={{ color: '#ffd700' }}>
            {resumo.razao_bf_vs_dijkstra}×
          </div>
          <div className={styles.statSub}>vezes mais lento</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>BF mais lento que BFS</div>
          <div className={styles.statVal} style={{ color: '#ffd700' }}>
            {resumo.razao_bf_vs_bfs}×
          </div>
          <div className={styles.statSub}>vezes mais lento</div>
        </div>
      </section>

      {/* ── Casos especiais Bellman-Ford ── */}
      <section className={styles.card}>
        <h2 className={styles.cardTitle}>Casos especiais — Bellman-Ford</h2>
        <div className={styles.bfGrid}>
          <div className={styles.bfCase}>
            <div className={styles.bfCaseTitle}>✅ Peso negativo sem ciclo</div>
            <div className={styles.bfDesc}>{casos.peso_negativo_sem_ciclo.descricao}</div>
            <div className={styles.bfPath}>
              Origem: <strong>{casos.peso_negativo_sem_ciclo.origem}</strong> →
              Destino: <strong>{casos.peso_negativo_sem_ciclo.destino}</strong>
            </div>
            <div className={styles.bfPath}>
              Caminho: {casos.peso_negativo_sem_ciclo.caminho.join(' → ')}
            </div>
            <div className={styles.bfPath}>
              Custo: <strong style={{ color: '#00e676' }}>{casos.peso_negativo_sem_ciclo.custo}</strong>
              {' '}· {casos.peso_negativo_sem_ciclo.tempo_ms} ms
            </div>
            <div className={styles.bfObs}>{casos.peso_negativo_sem_ciclo.observacao}</div>
          </div>
          <div className={styles.bfCase}>
            <div className={styles.bfCaseTitle}>⛔ Ciclo negativo detectado</div>
            <div className={styles.bfDesc}>{casos.ciclo_negativo_detectado.descricao}</div>
            <div className={styles.bfPath}>
              Custo do ciclo: <strong style={{ color: '#ff2d78' }}>{casos.ciclo_negativo_detectado.custo_do_ciclo}</strong>
            </div>
            <div className={styles.bfPath}>
              Detecção: <strong style={{ color: '#ff2d78' }}>
                {casos.ciclo_negativo_detectado.ciclo_negativo_detectado ? 'SIM' : 'NÃO'}
              </strong>
            </div>
            <div className={styles.bfObs}>{casos.ciclo_negativo_detectado.observacao}</div>
          </div>
        </div>
      </section>

      {/* ── Discussão crítica ── */}
      <section className={styles.card}>
        <h2 className={styles.cardTitle}>Discussão crítica</h2>
        <div className={styles.discuss}>
          {Object.entries(reportData.discussao_critica).map(([algo, texto]) => (
            <div key={algo} className={styles.discussItem}>
              <div className={styles.discussAlgo} style={{ color: algoColor(algo) }}>
                {algo}
              </div>
              <div className={styles.discussText}>{texto}</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
