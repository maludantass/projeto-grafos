import dijkstra1 from '../../../out/dijkstra_dataset2_f1_f2.json'
import dijkstra2 from '../../../out/dijkstra_dataset2_f1_f3.json'
import dijkstra3 from '../../../out/dijkstra_dataset2_f2_f3.json'
import bf1 from '../../../out/bellman_ford_dataset2_f1_f2.json'
import bf2 from '../../../out/bellman_ford_dataset2_f1_f3.json'
import bf3 from '../../../out/bellman_ford_dataset2_f2_f3.json'

import graphData from '../data/graph.json'
import { useState, useEffect, useRef, useMemo } from 'react'
import { runDijkstra, reconstructPath } from '../utils/dijkstra'
import { genreColor } from '../utils/genreColor'
import styles from './Comparacao.module.css'

const PAIRS = [
  { label: 'Par 1', dj: dijkstra1, bf: bf1 },
  { label: 'Par 2', dj: dijkstra2, bf: bf2 },
  { label: 'Par 3', dj: dijkstra3, bf: bf3 },
]

const nodeMap = new Map(graphData.nodes.map(n => [n.id, n]))
const getNode  = id => nodeMap.get(id)

// ── Busca de músicas inline ──────────────────────────────────────────────────
function SongSearch({ label, color, value, onSelect, placeholder }) {
  const [q, setQ]         = useState('')
  const [open, setOpen]   = useState(false)
  const wrapRef           = useRef(null)

  const results = useMemo(() => {
    if (!q.trim()) return []
    const lq = q.toLowerCase()
    return graphData.nodes
      .filter(n => n.name.toLowerCase().includes(lq) || n.artist.toLowerCase().includes(lq))
      .slice(0, 6)
  }, [q])

  useEffect(() => {
    function outside(e) { if (wrapRef.current && !wrapRef.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', outside)
    return () => document.removeEventListener('mousedown', outside)
  }, [])

  function pick(node) {
    setQ(node.name)
    setOpen(false)
    onSelect(node)
  }

  return (
    <div className={styles.songSearch} ref={wrapRef}>
      <div className={styles.ssLabel} style={{ color }}>{label}</div>
      <div className={styles.ssWrap}>
        <input
          className={styles.ssInput}
          style={{ borderColor: value ? color + '66' : undefined }}
          placeholder={placeholder}
          value={q}
          onChange={e => { setQ(e.target.value); setOpen(true); if (!e.target.value) onSelect(null) }}
          onFocus={() => setOpen(true)}
        />
        {value && <span className={styles.ssTick} style={{ color }}>✓</span>}
      </div>
      {open && results.length > 0 && (
        <div className={styles.ssDropdown}>
          {results.map(n => (
            <div key={n.id} className={styles.ssItem} onMouseDown={() => pick(n)}>
              <span className={styles.ssDot} style={{ background: genreColor(n.genre) }} />
              <div>
                <div className={styles.ssName}>{n.name}</div>
                <div className={styles.ssSub}>{n.artist} · {n.genre}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Popup de detalhe do nó ───────────────────────────────────────────────────
function NodeDetail({ node, color, onClose }) {
  if (!node) return null
  return (
    <div className={styles.nodePopup}>
      <button className={styles.nodePopupClose} onClick={onClose}>✕</button>
      <div className={styles.npDot} style={{ background: genreColor(node.genre) }} />
      <div className={styles.npName}>{node.name}</div>
      <div className={styles.npArtist}>{node.artist}</div>
      <div className={styles.npMeta}>
        <span className={styles.npTag} style={{ background: genreColor(node.genre) + '22', color: genreColor(node.genre) }}>{node.genre}</span>
        <span className={styles.npStat}>popularidade: <strong style={{ color }}>{node.popularity}</strong></span>
        <span className={styles.npStat}>grau: <strong style={{ color }}>{node.degree}</strong></span>
      </div>
    </div>
  )
}

// ── Barra de velocidade animada ──────────────────────────────────────────────
function SpeedBar({ label, value, max, color }) {
  const [pct, setPct] = useState(0)
  useEffect(() => {
    const t = setTimeout(() => setPct((value / max) * 100), 80)
    return () => clearTimeout(t)
  }, [value, max])
  return (
    <div className={styles.speedRow}>
      <div className={styles.speedLabel}>{label}</div>
      <div className={styles.speedTrack}>
        <div className={styles.speedFill} style={{ width: `${pct}%`, background: color }} />
        <span className={styles.speedValue}>{value.toFixed(3)} ms</span>
      </div>
    </div>
  )
}

// ── Card de algoritmo ────────────────────────────────────────────────────────
function AlgoCard({ algo, color, label, badge, animatedCount, onNodeClick, activeNode }) {
  const orig = getNode(algo.origem)
  const dest = getNode(algo.destino)
  const path = algo.caminho || []

  return (
    <div className={styles.algoCard} style={{ borderColor: color + '44' }}>
      <div className={styles.algoHeader}>
        <span className={styles.algoLabel} style={{ color }}>{label}</span>
        <span className={styles.algoBadge} style={{ color, borderColor: color + '44' }}>{badge}</span>
      </div>

      <div className={styles.algoStats}>
        <div className={styles.algoStat}>
          <div className={styles.algoStatV} style={{ color }}>{algo.custo != null ? algo.custo.toFixed(4) : '—'}</div>
          <div className={styles.algoStatL}>Custo total</div>
        </div>
        <div className={styles.algoStat}>
          <div className={styles.algoStatV}>{algo.saltos}</div>
          <div className={styles.algoStatL}>Saltos</div>
        </div>
        <div className={styles.algoStat}>
          <div className={styles.algoStatV}>{algo.tempo_ms.toFixed(2)} ms</div>
          <div className={styles.algoStatL}>Tempo</div>
        </div>
      </div>

      <div className={styles.endpoints}>
        <div className={styles.endpoint}>
          <div className={styles.epBadge} style={{ background: color + '22', color }}>ORIGEM</div>
          <div className={styles.epName}>{orig?.name ?? algo.musica_origem}</div>
          <div className={styles.epArtist}>{orig?.artist}</div>
        </div>
        <div className={styles.arrow}>→</div>
        <div className={styles.endpoint}>
          <div className={styles.epBadge} style={{ background: color + '22', color }}>DESTINO</div>
          <div className={styles.epName}>{dest?.name ?? algo.musica_destino}</div>
          <div className={styles.epArtist}>{dest?.artist}</div>
        </div>
      </div>

      <div className={styles.path}>
        <div className={styles.pathTitle}>
          Caminho encontrado
          <span className={styles.pathHint}>clique em um nó para ver detalhes</span>
        </div>
        {path.length === 0 ? (
          <div className={styles.noPath}>Sem caminho (componentes desconexos)</div>
        ) : (
          <div className={styles.pathNodes}>
            {path.slice(0, animatedCount).map((id, i) => {
              const n = getNode(id)
              const isEndpoint = i === 0 || i === path.length - 1
              const isActive   = activeNode?.id === id
              return (
                <span key={id} className={styles.pathNodeWrap}>
                  <span
                    className={`${styles.pathNode} ${isActive ? styles.pathNodeActive : ''}`}
                    style={{
                      borderColor: isEndpoint ? color : color + '55',
                      color: isEndpoint ? color : 'rgba(255,255,255,0.75)',
                      background: isActive ? color + '22' : undefined,
                    }}
                    onClick={() => onNodeClick(n || { id, name: id, artist: '', genre: '', popularity: 0, degree: 0 })}
                    title="Clique para ver detalhes"
                  >
                    {n ? n.name.slice(0, 14) : id.slice(0, 8)}
                  </span>
                  {i < animatedCount - 1 && i < path.length - 1 && (
                    <span className={styles.pathArrow}>→</span>
                  )}
                </span>
              )
            })}
            {animatedCount < path.length && (
              <span className={styles.pathLoading}>…</span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// ── Página principal ─────────────────────────────────────────────────────────
export default function Comparacao() {
  const [idx,          setIdx]          = useState(0)
  const [customMode,   setCustomMode]   = useState(false)
  const [srcNode,      setSrcNode]      = useState(null)
  const [dstNode,      setDstNode]      = useState(null)
  const [customResult, setCustomResult] = useState(null)
  const [calculating,  setCalculating]  = useState(false)
  const [animCount,    setAnimCount]    = useState(0)
  const [detailNode,   setDetailNode]   = useState(null)
  const [detailColor,  setDetailColor]  = useState('#ffd700')

  const par = customMode ? customResult : PAIRS[idx]

  // Anima o caminho toda vez que o par ou modo muda
  const pathLen = par?.dj?.caminho?.length ?? 0
  useEffect(() => {
    setAnimCount(0)
    setDetailNode(null)
    if (!pathLen) return
    let i = 0
    const id = setInterval(() => {
      i++
      setAnimCount(i)
      if (i >= pathLen) clearInterval(id)
    }, 55)
    return () => clearInterval(id)
  }, [idx, customResult, pathLen])

  function handleNodeClick(node, color) {
    setDetailNode(prev => prev?.id === node.id ? null : node)
    setDetailColor(color)
  }

  function handleCalculate() {
    if (!srcNode || !dstNode) return
    setCalculating(true)
    setCustomResult(null)
    setTimeout(() => {
      const t0 = performance.now()
      const { dist, prev } = runDijkstra(graphData.nodes, graphData.edges.map(e => ({ ...e })), srcNode.id)
      const path    = reconstructPath(prev, srcNode.id, dstNode.id)
      const elapsed = performance.now() - t0
      const custo   = path ? dist.get(dstNode.id) : null
      setCustomResult({
        dj: {
          algoritmo: 'Dijkstra', origem: srcNode.id, destino: dstNode.id,
          musica_origem: srcNode.name, musica_destino: dstNode.name,
          custo, caminho: path || [], saltos: path ? path.length - 1 : 0,
          tempo_ms: Math.round(elapsed * 1000) / 1000,
        },
        bf: null,
      })
      setCalculating(false)
    }, 20)
  }

  const concordam = !customMode && par
    ? par.dj.custo?.toFixed(6) === par.bf?.custo?.toFixed(6)
    : null

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Dijkstra vs Bellman-Ford</h1>
      <p className={styles.subtitle}>
        Comparação dos caminhos mínimos. Como os pesos são distâncias euclidianas (≥ 0),
        ambos produzem o mesmo resultado — mas com desempenhos muito diferentes.
      </p>

      {/* Seletor de modo */}
      <div className={styles.modeRow}>
        <button
          className={`${styles.modeBtn} ${!customMode ? styles.modeBtnActive : ''}`}
          onClick={() => { setCustomMode(false); setDetailNode(null) }}
        >
          Pares pré-computados
        </button>
        <button
          className={`${styles.modeBtn} ${customMode ? styles.modeBtnActive : ''}`}
          onClick={() => { setCustomMode(true); setDetailNode(null) }}
        >
          ✦ Par personalizado
        </button>
      </div>

      {/* Modo pré-computado */}
      {!customMode && (
        <div className={styles.pairRow}>
          {PAIRS.map((p, i) => {
            const o = getNode(p.dj.origem)
            const d = getNode(p.dj.destino)
            return (
              <button
                key={i}
                className={`${styles.pairBtn} ${idx === i ? styles.pairBtnActive : ''}`}
                onClick={() => { setIdx(i); setDetailNode(null) }}
              >
                <span className={styles.pairNum}>{p.label}</span>
                <span className={styles.pairSongs}>
                  {o?.name?.slice(0, 12) ?? '?'} → {d?.name?.slice(0, 12) ?? '?'}
                </span>
              </button>
            )
          })}
        </div>
      )}

      {/* Modo personalizado */}
      {customMode && (
        <div className={styles.customPanel}>
          <div className={styles.customSearches}>
            <SongSearch
              label="Origem" color="#ffd700" value={srcNode}
              placeholder="Buscar música de origem…"
              onSelect={setSrcNode}
            />
            <div className={styles.customArrow}>→</div>
            <SongSearch
              label="Destino" color="#ff2d78" value={dstNode}
              placeholder="Buscar música de destino…"
              onSelect={setDstNode}
            />
          </div>
          <button
            className={`${styles.calcBtn} ${(!srcNode || !dstNode || calculating) ? styles.calcBtnDisabled : ''}`}
            onClick={handleCalculate}
            disabled={!srcNode || !dstNode || calculating}
          >
            {calculating ? '⟳ Calculando…' : '▶ Calcular caminho'}
          </button>
          {customMode && !customResult && !calculating && (
            <p className={styles.customHint}>
              Selecione duas músicas e clique em Calcular. Dijkstra roda no browser em ~50ms.
              Bellman-Ford (O(V×E) ≈ 79M ops) usa os resultados pré-computados nos pares fixos.
            </p>
          )}
        </div>
      )}

      {/* Conteúdo do par selecionado */}
      {par && (
        <>
          {/* Banner de concordância (só pares pré-computados) */}
          {concordam !== null && (
            <div className={`${styles.banner} ${concordam ? styles.bannerOk : styles.bannerFail}`}>
              {concordam
                ? '✅ Ambos os algoritmos concordam — mesmo custo mínimo encontrado'
                : '⚠️ Algoritmos divergem nos resultados'}
            </div>
          )}
          {customMode && customResult && (
            <div className={`${styles.banner} ${styles.bannerInfo}`}>
              ℹ️ Modo personalizado: Dijkstra calculado no browser. Bellman-Ford não disponível (muito lento para 4000 nós em tempo real).
            </div>
          )}

          {/* Popup de detalhe do nó */}
          {detailNode && (
            <NodeDetail node={detailNode} color={detailColor} onClose={() => setDetailNode(null)} />
          )}

          {/* Cards lado a lado */}
          <div className={styles.side2}>
            <AlgoCard
              algo={par.dj}
              color="#ffd700"
              label="Dijkstra"
              badge="O((V+E) log V) · Heap binário"
              animatedCount={animCount}
              onNodeClick={n => handleNodeClick(n, '#ffd700')}
              activeNode={detailNode}
            />
            {par.bf ? (
              <AlgoCard
                algo={par.bf}
                color="#00e676"
                label="Bellman-Ford"
                badge="O(V×E) · Relaxamentos iterativos"
                animatedCount={animCount}
                onNodeClick={n => handleNodeClick(n, '#00e676')}
                activeNode={detailNode}
              />
            ) : (
              <div className={styles.bfUnavailable}>
                <div className={styles.bfUnavLabel}>Bellman-Ford</div>
                <div className={styles.bfUnavMsg}>
                  Não disponível para pares personalizados em tempo real.
                </div>
                <div className={styles.bfUnavNote}>
                  O(V×E) = O(4000 × 19717) ≈ 79 milhões de operações.
                  Use os pares pré-computados para ver a comparação completa.
                </div>
              </div>
            )}
          </div>

          {/* Comparativo de velocidade */}
          {par.bf && (
            <div className={styles.card}>
              <div className={styles.cardTitle}>Comparativo de velocidade</div>
              <div className={styles.speedCompare}>
                <SpeedBar label="Dijkstra"      value={par.dj.tempo_ms} max={Math.max(par.dj.tempo_ms, par.bf.tempo_ms)} color="#ffd700" />
                <SpeedBar label="Bellman-Ford"  value={par.bf.tempo_ms} max={Math.max(par.dj.tempo_ms, par.bf.tempo_ms)} color="#00e676" />
              </div>
              <div className={styles.ratioRow}>
                <div className={styles.ratioVal}>{(par.bf.tempo_ms / par.dj.tempo_ms).toFixed(1)}×</div>
                <div className={styles.ratioDesc}>
                  Bellman-Ford foi <strong>{(par.bf.tempo_ms / par.dj.tempo_ms).toFixed(1)}×</strong> mais lento.
                  Para grafos com pesos ≥ 0, Dijkstra é sempre preferível. Bellman-Ford é indispensável
                  apenas com pesos negativos ou para detectar ciclos negativos.
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
