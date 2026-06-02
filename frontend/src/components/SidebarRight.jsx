import { useMemo } from 'react'
import graphData from '../data/graph.json'
import { genreColor } from '../utils/genreColor'
import styles from './SidebarRight.module.css'

export default function SidebarRight({
  selectedNode, activeGenre, setActiveGenre,
  strength, setStrength, pathMode, setPathMode,
}) {
  const destaques = useMemo(() => {
    const maxDeg = graphData.nodes.reduce((a, b) => a.degree > b.degree ? a : b)
    const gc = {}
    graphData.nodes.forEach(n => { gc[n.genre] = (gc[n.genre] || 0) + 1 })
    const topGenre = Object.entries(gc).sort((a, b) => b[1] - a[1])[0][0]
    const grauMedio = (graphData.nodes.reduce((s, n) => s + n.degree, 0) / graphData.nodes.length).toFixed(2)
    return { maxDeg, topGenre, grauMedio }
  }, [])

  const visibleDegree = useMemo(() => {
    if (!selectedNode) return 0
    const threshold = strength / 100
    return graphData.edges.filter(
      e => e.value >= threshold &&
        (e.source === selectedNode.id || e.target === selectedNode.id)
    ).length
  }, [selectedNode, strength])

  const pct = strength

  return (
    <aside className={styles.sidebar}>
      <div className={styles.header}>
        <div className={styles.dot} />
        CONTROLE DA REDE
      </div>

      <div className={styles.section}>
        <button
          className={`${styles.dijkstraBtn} ${pathMode ? styles.dijkstraBtnActive : ''}`}
          onClick={() => setPathMode(p => !p)}
        >
          ⇢ Caminho Dijkstra
        </button>
      </div>

      <div className={styles.section}>
        <div className={styles.label}>Filtrar por gênero</div>
        <select
          className={styles.select}
          value={activeGenre || ''}
          onChange={e => setActiveGenre(e.target.value || null)}
        >
          <option value="">Todos os gêneros</option>
          {[...new Set(graphData.nodes.map(n => n.genre))].sort().map(g => (
            <option key={g} value={g}>{g}</option>
          ))}
        </select>
      </div>

      <div className={styles.section}>
        <div className={styles.label}>Similaridade mínima</div>
        <div className={styles.rangeWrap}>
          <input
            type="range" min={0} max={80} value={strength}
            className={styles.range}
            style={{ background: `linear-gradient(to right, var(--green) ${(strength/80)*100}%, rgba(255,255,255,.1) ${(strength/80)*100}%)` }}
            onChange={e => setStrength(Number(e.target.value))}
          />
          <span className={styles.rangeVal}>{strength}%</span>
        </div>
        <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.3)', marginTop: 4 }}>
          só exibe conexões com ≥{strength}% de similaridade
        </div>
      </div>

      {selectedNode ? (
        <div className={styles.section}>
          <div className={styles.label}>Música selecionada</div>
          <div className={styles.ndName}>{selectedNode.name}</div>
          <div className={styles.ndArtist}>{selectedNode.artist}</div>
          <span
            className={styles.ndGenre}
            style={{ background: genreColor(selectedNode.genre) + '22', color: genreColor(selectedNode.genre) }}
          >
            {selectedNode.genre}
          </span>
          <div className={styles.ndStats}>
            <div className={styles.ndStat}>
              <div className={styles.ndStatV} style={{ color: 'var(--green)' }}>{visibleDegree}</div>
              <div className={styles.ndStatL}>conexões visíveis</div>
            </div>
            <div className={styles.ndStat}>
              <div className={styles.ndStatV} style={{ color: 'var(--purple)' }}>{selectedNode.popularity}</div>
              <div className={styles.ndStatL}>popularidade</div>
            </div>
          </div>
        </div>
      ) : (
        <div className={styles.section}>
          <div className={styles.label}>Destaques</div>
          <div className={styles.destList}>
            <div className={styles.destItem}>
              <div className={`${styles.destIco} ${styles.hub}`}>👑</div>
              <div>
                <div className={styles.destTitle}>MAIOR HUB</div>
                <div className={styles.destVal}>{destaques.maxDeg.artist}</div>
              </div>
            </div>
            <div className={styles.destItem}>
              <div className={`${styles.destIco} ${styles.com}`}>◉</div>
              <div>
                <div className={styles.destTitle}>MAIOR COMUNIDADE</div>
                <div className={styles.destVal}>{destaques.topGenre}</div>
              </div>
            </div>
            <div className={styles.destItem}>
              <div className={`${styles.destIco} ${styles.path}`}>⇢</div>
              <div>
                <div className={styles.destTitle}>GRAU MÉDIO</div>
                <div className={styles.destVal}>{destaques.grauMedio} conexões</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </aside>
  )
}
