import { useState, useMemo, useEffect, useCallback } from 'react'
import { genreColor } from '../utils/genreColor'
import graphData from '../data/graph.json'

import bfsData1 from '../../../out/bfs_dataset2.json'
import bfsData2 from '../../../out/bfs_dataset2_f2.json'
import bfsData3 from '../../../out/bfs_dataset2_f3.json'

import dfsData1 from '../../../out/dfs_dataset2.json'
import dfsData2 from '../../../out/dfs_dataset2_f2.json'
import dfsData3 from '../../../out/dfs_dataset2_f3.json'

import styles from './Visualizacoes.module.css'

const BFS_SOURCES = [bfsData1, bfsData2, bfsData3]
const DFS_SOURCES = [dfsData1, dfsData2, dfsData3]

const LEVEL_COLORS = [
  '#00e676', '#69f0ae', '#b9f6ca',
  '#ffd740', '#ffab40', '#ff6d00',
  '#ff4081', '#ea80fc', '#b388ff',
  '#82b1ff', '#80d8ff', '#a7ffeb',
]

const nodeMap = new Map(graphData.nodes.map(n => [n.id, n]))

function getNodeName(id) {
  const n = nodeMap.get(id)
  return n ? `${n.name} — ${n.artist}` : id.slice(0, 10) + '...'
}

export default function Visualizacoes() {
  const [tab,    setTab]    = useState('bfs')
  const [bfsIdx, setBfsIdx] = useState(0)
  const [dfsIdx, setDfsIdx] = useState(0)

  // BFS animation
  const [playing,    setPlaying]    = useState(false)
  const [revealedTo, setRevealedTo] = useState(null) // null = all; number = index of last visible level
  const [speed,      setSpeed]      = useState(700)

  // Expanded levels (show all nodes, not just 8)
  const [expandedLevels, setExpandedLevels] = useState(new Set())

  // Clicked node detail
  const [nodeDetail, setNodeDetail] = useState(null)

  // Search
  const [bfsSearch, setBfsSearch] = useState('')
  const [dfsSearch, setDfsSearch] = useState('')

  const bfs = BFS_SOURCES[bfsIdx]
  const dfs = DFS_SOURCES[dfsIdx]

  // Reset animation on source / tab change
  useEffect(() => {
    setRevealedTo(null)
    setPlaying(false)
    setExpandedLevels(new Set())
    setNodeDetail(null)
    setBfsSearch('')
  }, [tab, bfsIdx])

  useEffect(() => {
    setDfsSearch('')
    setNodeDetail(null)
  }, [dfsIdx])

  // Animation interval
  useEffect(() => {
    if (!playing) return
    const maxLevel = bfs.camadas.length - 1
    const id = setInterval(() => {
      setRevealedTo(prev => {
        const cur = prev ?? -1
        if (cur >= maxLevel) {
          setPlaying(false)
          return null
        }
        return cur + 1
      })
    }, speed)
    return () => clearInterval(id)
  }, [playing, bfs.camadas.length, speed])

  const startAnimation = useCallback(() => {
    setRevealedTo(0)
    setPlaying(true)
  }, [])

  const stepBackward = useCallback(() => {
    setRevealedTo(prev => (prev === null || prev === 0) ? 0 : prev - 1)
    setPlaying(false)
  }, [])

  const stepForward = useCallback(() => {
    const max = bfs.camadas.length - 1
    setRevealedTo(prev => {
      const cur = prev === null ? max : prev
      return Math.min(cur + 1, max)
    })
    setPlaying(false)
  }, [bfs.camadas.length])

  const resetAnimation = useCallback(() => {
    setRevealedTo(null)
    setPlaying(false)
  }, [])

  function toggleLevel(nivel) {
    setExpandedLevels(prev => {
      const next = new Set(prev)
      next.has(nivel) ? next.delete(nivel) : next.add(nivel)
      return next
    })
  }

  function handleNodeClick(id, nivel) {
    const n = nodeMap.get(id)
    if (!n) return
    setNodeDetail(prev =>
      prev?.id === id ? null : { ...n, nivel }
    )
  }

  const isAnimating   = revealedTo !== null
  const levelsToShow  = isAnimating ? bfs.camadas.slice(0, revealedTo + 1) : bfs.camadas

  const dfsEdgeCounts = useMemo(() => {
    const get = v => typeof v === 'number' ? v : (Array.isArray(v) ? v.length : 0)
    return {
      arvore:  get(dfs.arestas_tipo.arvore),
      retorno: get(dfs.arestas_tipo.retorno),
      avanco:  get(dfs.arestas_tipo.avanco),
      cruzada: get(dfs.arestas_tipo.cruzada),
    }
  }, [dfs])

  // Filtered visit orders
  const filteredBfsVisit = useMemo(() => {
    const q = bfsSearch.trim().toLowerCase()
    if (!q) return bfs.ordem_visita.slice(0, 30)
    return bfs.ordem_visita.filter(id => {
      const n = nodeMap.get(id)
      return n?.name?.toLowerCase().includes(q) || n?.artist?.toLowerCase().includes(q)
    }).slice(0, 60)
  }, [bfs.ordem_visita, bfsSearch])

  const filteredDfsVisit = useMemo(() => {
    const q = dfsSearch.trim().toLowerCase()
    if (!q) return dfs.ordem_visita.slice(0, 30)
    return dfs.ordem_visita.filter(id => {
      const n = nodeMap.get(id)
      return n?.name?.toLowerCase().includes(q) || n?.artist?.toLowerCase().includes(q)
    }).slice(0, 60)
  }, [dfs.ordem_visita, dfsSearch])

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Visualizações de Algoritmos</h1>

      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${tab === 'bfs' ? styles.tabActive : ''}`}
          onClick={() => setTab('bfs')}
        >
          BFS — Busca em Largura
        </button>
        <button
          className={`${styles.tab} ${tab === 'dfs' ? styles.tabActive : ''}`}
          onClick={() => setTab('dfs')}
        >
          DFS — Busca em Profundidade
        </button>
      </div>

      {/* ════════════════ BFS ════════════════ */}
      {tab === 'bfs' && (
        <div>
          <div className={styles.sourceRow}>
            <span className={styles.sourceLabel}>Nó de origem:</span>
            {BFS_SOURCES.map((b, i) => (
              <button
                key={i}
                className={`${styles.srcBtn} ${bfsIdx === i ? styles.srcBtnActive : ''}`}
                onClick={() => setBfsIdx(i)}
              >
                {getNodeName(b.origem).slice(0, 32)}
              </button>
            ))}
          </div>

          <div className={styles.statsRow}>
            <div className={styles.stat}>
              <div className={styles.statV}>{bfs.nos_visitados}</div>
              <div className={styles.statL}>Nós visitados</div>
            </div>
            <div className={styles.stat}>
              <div className={styles.statV}>{bfs.nivel_maximo}</div>
              <div className={styles.statL}>Nível máximo</div>
            </div>
            <div className={styles.stat}>
              <div className={styles.statV}>{bfs.tempo_ms.toFixed(2)} ms</div>
              <div className={styles.statL}>Tempo</div>
            </div>
            <div className={styles.stat}>
              <div className={styles.statV} style={{ fontSize: '0.85rem' }}>{getNodeName(bfs.origem)}</div>
              <div className={styles.statL}>Origem</div>
            </div>
          </div>

          {/* Detalhe do nó clicado */}
          {nodeDetail && (
            <div className={styles.nodeDetailBar}>
              <div className={styles.nodeDetailDot} style={{ background: genreColor(nodeDetail.genre) }} />
              <div className={styles.nodeDetailInfo}>
                <div className={styles.nodeDetailName}>{nodeDetail.name}</div>
                <div className={styles.nodeDetailMeta}>
                  {nodeDetail.artist} · {nodeDetail.genre} · Popularidade: {nodeDetail.popularity} · Nível BFS: <strong style={{ color: LEVEL_COLORS[nodeDetail.nivel % LEVEL_COLORS.length] }}>{nodeDetail.nivel}</strong>
                </div>
              </div>
              <button className={styles.nodeDetailClose} onClick={() => setNodeDetail(null)}>✕</button>
            </div>
          )}

          {/* Camadas com controles de animação */}
          <div className={styles.card}>
            <div className={styles.cardTitle}>Árvore BFS — Camadas por nível</div>

            <div className={styles.animControls}>
              {!playing ? (
                <button className={`${styles.playBtn} ${styles.playBtnPlay}`} onClick={startAnimation}>
                  ▶ Animar
                </button>
              ) : (
                <button className={`${styles.playBtn} ${styles.playBtnPause}`} onClick={() => setPlaying(false)}>
                  ⏸ Pausar
                </button>
              )}
              <button
                className={styles.stepBtn}
                onClick={stepBackward}
                disabled={!isAnimating || revealedTo === 0}
              >◀ Anterior</button>
              <button
                className={styles.stepBtn}
                onClick={stepForward}
                disabled={isAnimating && revealedTo >= bfs.camadas.length - 1}
              >Próximo ▶</button>
              <button className={styles.resetBtn} onClick={resetAnimation}>↺ Ver todos</button>
              <select
                className={styles.speedSelect}
                value={speed}
                onChange={e => setSpeed(Number(e.target.value))}
              >
                <option value={300}>Rápido</option>
                <option value={700}>Normal</option>
                <option value={1400}>Lento</option>
              </select>
              <span className={styles.levelProgress}>
                {isAnimating
                  ? `Nível ${revealedTo} / ${bfs.camadas.length - 1}`
                  : `${bfs.camadas.length} níveis · clique nos nós para detalhes`}
              </span>
            </div>

            <div className={styles.bfsLevels}>
              {levelsToShow.map((camada, nivel) => {
                const isCurrentLevel = isAnimating && nivel === revealedTo
                const expanded       = expandedLevels.has(nivel)
                const color          = LEVEL_COLORS[nivel % LEVEL_COLORS.length]
                const displayNodes   = expanded ? camada : camada.slice(0, 8)

                return (
                  <div
                    key={nivel}
                    className={`${styles.bfsLevel} ${isCurrentLevel ? styles.bfsLevelCurrent : ''}`}
                  >
                    <div
                      className={styles.bfsLevelBadge}
                      style={{
                        background:  color + '22',
                        color:        color,
                        borderColor:  color + '55',
                        boxShadow:    isCurrentLevel ? `0 0 14px ${color}55` : 'none',
                      }}
                    >
                      Nível {nivel}
                      <span className={styles.bfsLevelCount}>{camada.length} nós</span>
                    </div>

                    <div className={styles.bfsNodes}>
                      {displayNodes.map(id => {
                        const n = nodeMap.get(id)
                        const isSelected = nodeDetail?.id === id
                        return (
                          <div
                            key={id}
                            className={`${styles.bfsNode} ${isSelected ? styles.bfsNodeSelected : ''}`}
                            style={{
                              borderColor: isSelected ? color : color + '55',
                              background:  isSelected ? color + '22' : undefined,
                              cursor: 'pointer',
                            }}
                            title={n ? `${n.name} — ${n.artist} (${n.genre})` : id}
                            onClick={() => handleNodeClick(id, nivel)}
                          >
                            <div className={styles.bfsNodeDot} style={{ background: n ? genreColor(n.genre) : '#aaa' }} />
                            <span>{n ? n.name.slice(0, 16) : id.slice(0, 10)}</span>
                          </div>
                        )
                      })}
                      {camada.length > 8 && (
                        <button className={styles.expandBtn} onClick={() => toggleLevel(nivel)}>
                          {expanded ? '▲ menos' : `+${camada.length - 8} mais`}
                        </button>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Ordem de visita com busca */}
          <div className={styles.card}>
            <div className={styles.cardTitle}>Ordem de visita BFS</div>
            <div className={styles.searchRow}>
              <input
                className={styles.searchInput}
                placeholder="Buscar música ou artista…"
                value={bfsSearch}
                onChange={e => setBfsSearch(e.target.value)}
              />
              <span className={styles.searchCount}>
                {bfsSearch ? `${filteredBfsVisit.length} resultado(s)` : `primeiros 30 de ${bfs.nos_visitados}`}
              </span>
            </div>
            <div className={styles.visitOrder}>
              {filteredBfsVisit.map(id => {
                const n      = nodeMap.get(id)
                const nivel  = bfs.niveis[id] ?? '?'
                const rank   = bfs.ordem_visita.indexOf(id)
                return (
                  <div
                    key={id}
                    className={`${styles.visitItem} ${nodeDetail?.id === id ? styles.visitItemSelected : ''}`}
                    onClick={() => handleNodeClick(id, nivel)}
                  >
                    <span className={styles.visitNum}>{rank + 1}</span>
                    <div className={styles.visitDot} style={{ background: LEVEL_COLORS[nivel % LEVEL_COLORS.length] }} />
                    <div className={styles.visitInfo}>
                      <div className={styles.visitName}>{n ? n.name : id.slice(0, 10)}</div>
                      <div className={styles.visitMeta}>{n?.artist} · Nível {nivel} · {n?.genre}</div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* ════════════════ DFS ════════════════ */}
      {tab === 'dfs' && (
        <div>
          <div className={styles.sourceRow}>
            <span className={styles.sourceLabel}>Nó de origem:</span>
            {DFS_SOURCES.map((d, i) => (
              <button
                key={i}
                className={`${styles.srcBtn} ${dfsIdx === i ? styles.srcBtnActive : ''}`}
                onClick={() => setDfsIdx(i)}
              >
                {getNodeName(d.origem).slice(0, 32)}
              </button>
            ))}
          </div>

          <div className={styles.statsRow}>
            <div className={styles.stat}>
              <div className={styles.statV}>{dfs.nos_visitados}</div>
              <div className={styles.statL}>Nós visitados</div>
            </div>
            <div className={styles.stat}>
              <div className={styles.statV} style={{ color: dfs.tem_ciclo ? '#ff2d78' : '#00e676' }}>
                {dfs.tem_ciclo ? 'Sim' : 'Não'}
              </div>
              <div className={styles.statL}>Ciclo detectado</div>
            </div>
            <div className={styles.stat}>
              <div className={styles.statV}>{dfs.tempo_ms.toFixed(2)} ms</div>
              <div className={styles.statL}>Tempo</div>
            </div>
          </div>

          {/* Detalhe do nó clicado */}
          {nodeDetail && (
            <div className={styles.nodeDetailBar}>
              <div className={styles.nodeDetailDot} style={{ background: genreColor(nodeDetail.genre) }} />
              <div className={styles.nodeDetailInfo}>
                <div className={styles.nodeDetailName}>{nodeDetail.name}</div>
                <div className={styles.nodeDetailMeta}>
                  {nodeDetail.artist} · {nodeDetail.genre} · Popularidade: {nodeDetail.popularity}
                  {' '}· entrada: {dfs.tempo_entrada[nodeDetail.id]} · saída: {dfs.tempo_saida[nodeDetail.id]}
                </div>
              </div>
              <button className={styles.nodeDetailClose} onClick={() => setNodeDetail(null)}>✕</button>
            </div>
          )}

          {/* Classificação de arestas */}
          <div className={styles.card}>
            <div className={styles.cardTitle}>Classificação de arestas</div>
            <p className={styles.cardDesc}>
              O DFS classifica cada aresta encontrada. Arestas de retorno indicam ciclos no grafo.
            </p>
            <div className={styles.edgeGrid}>
              {[
                { tipo: 'Árvore',  count: dfsEdgeCounts.arvore,  color: '#00e676', desc: 'Avançam para nós não visitados — formam a árvore DFS.' },
                { tipo: 'Retorno', count: dfsEdgeCounts.retorno, color: '#ff2d78', desc: 'Voltam para um ancestral — indicam ciclos.' },
                { tipo: 'Avanço',  count: dfsEdgeCounts.avanco,  color: '#ffd700', desc: 'Para descendentes já terminados (grafos dirigidos).' },
                { tipo: 'Cruzada', count: dfsEdgeCounts.cruzada, color: '#d500f9', desc: 'Entre ramos diferentes da árvore DFS.' },
              ].map(e => (
                <div key={e.tipo} className={styles.edgeCard} style={{ borderColor: e.color + '44' }}>
                  <div className={styles.edgeCount} style={{ color: e.color }}>{e.count.toLocaleString('pt-BR')}</div>
                  <div className={styles.edgeType}  style={{ color: e.color }}>{e.tipo}</div>
                  <div className={styles.edgeDesc}>{e.desc}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Ordem de visita DFS com busca */}
          <div className={styles.card}>
            <div className={styles.cardTitle}>Ordem de visita DFS</div>
            <p className={styles.cardDesc}>
              O DFS explora o mais fundo possível antes de retroceder. Nós consecutivos tendem a ser mais relacionados entre si do que no BFS.
            </p>
            <div className={styles.searchRow}>
              <input
                className={styles.searchInput}
                placeholder="Buscar música ou artista…"
                value={dfsSearch}
                onChange={e => setDfsSearch(e.target.value)}
              />
              <span className={styles.searchCount}>
                {dfsSearch ? `${filteredDfsVisit.length} resultado(s)` : `primeiros 30 de ${dfs.nos_visitados}`}
              </span>
            </div>
            <div className={styles.visitOrder}>
              {filteredDfsVisit.map(id => {
                const n       = nodeMap.get(id)
                const entTime = dfs.tempo_entrada[id]
                const saiTime = dfs.tempo_saida[id]
                const rank    = dfs.ordem_visita.indexOf(id)
                return (
                  <div
                    key={id}
                    className={`${styles.visitItem} ${nodeDetail?.id === id ? styles.visitItemSelected : ''}`}
                    onClick={() => handleNodeClick(id, null)}
                  >
                    <span className={styles.visitNum}>{rank + 1}</span>
                    <div className={styles.visitDot} style={{ background: '#d500f9' }} />
                    <div className={styles.visitInfo}>
                      <div className={styles.visitName}>{n ? n.name : id.slice(0, 10)}</div>
                      <div className={styles.visitMeta}>
                        {n?.artist} · entrada: {entTime} · saída: {saiTime}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
