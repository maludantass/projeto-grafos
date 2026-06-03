import { useMemo, useState, useCallback, useEffect, useRef } from 'react'
import graphData from '../data/graph.json'
import { genreColor } from '../utils/genreColor'
import styles from './SidebarLeft.module.css'

const PLAYLIST = [
  { id: '6LsAAHotRLMOHfCsSfYCsz', name: "If I Can't Have You", artist: 'Shawn Mendes' },
  { id: '4LRPiXqCikLlN15c3yImP7', name: 'As It Was',           artist: 'Harry Styles'  },
  { id: '3w3y8KPTfNeOKPiqUTakBh', name: 'Locked Out of Heaven', artist: 'Bruno Mars'   },
  { id: '3xKsf9qdS1CyvXSMEid6g8', name: 'Pink + White',         artist: 'Frank Ocean'  },
  { id: '6RwSREtb8zda5Xj8XvUyu7', name: 'Cacos',                artist: 'Matheus & Kauan' },
]

const NAV_ITEMS = [
  { id: 'landing',    icon: '⌂',  label: 'INÍCIO' },
  { id: 'explore',    icon: '⚡',  label: 'EXPLORAR REDE' },
  { id: 'benchmark',  icon: '⬡',  label: 'BENCHMARK' },
  { id: 'viz',        icon: '▦',  label: 'BFS / DFS' },
  { id: 'comparacao', icon: '⇢',  label: 'DIJKSTRA vs BF' },
  { id: 'sobre',      icon: 'ℹ',  label: 'SOBRE O PROJETO' },
]

export default function SidebarLeft({ page, setPage, activeGenre, setActiveGenre }) {
  const [genreSearch, setGenreSearch] = useState('')
  const [trackIdx, setTrackIdx]   = useState(0)
  const trackIdxRef   = useRef(0)
  const controllerRef = useRef(null)
  const containerRef  = useRef(null)
  const advancedRef   = useRef(false) // evita avanço duplo por múltiplos eventos no fim da faixa

  // Carrega a Spotify Iframe API — detecta fim de faixa via playback_update
  useEffect(() => {
    const script = document.createElement('script')
    script.src = 'https://open.spotify.com/embed/iframe-api/v1'
    script.async = true
    document.head.appendChild(script)

    window.onSpotifyIframeApiReady = (IFrameAPI) => {
      if (!containerRef.current) return
      IFrameAPI.createController(
        containerRef.current,
        { uri: `spotify:track:${PLAYLIST[0].id}`, width: '100%', height: '80' },
        (controller) => {
          controllerRef.current = controller
          controller.addListener('playback_update', ({ data }) => {
            const { isPaused, position, duration } = data
            // Nova faixa começou: reseta o flag de avanço
            if (position < 1500) advancedRef.current = false
            // Fim de faixa detectado — avança uma única vez
            if (!isPaused && duration > 0 && position >= duration - 800 && !advancedRef.current) {
              advancedRef.current = true
              const next = (trackIdxRef.current + 1) % PLAYLIST.length
              trackIdxRef.current = next
              setTrackIdx(next)
              controller.loadUri(`spotify:track:${PLAYLIST[next].id}`)
              setTimeout(() => controller.play(), 400)
            }
          })
        }
      )
    }
    return () => { script.remove(); delete window.onSpotifyIframeApiReady }
  }, [])

  const changeTrack = useCallback((idx) => {
    trackIdxRef.current = idx
    setTrackIdx(idx)
    const c = controllerRef.current
    if (c) { c.loadUri(`spotify:track:${PLAYLIST[idx].id}`); setTimeout(() => c.play(), 350) }
  }, [])

  const prevTrack = useCallback(() => changeTrack((trackIdxRef.current - 1 + PLAYLIST.length) % PLAYLIST.length), [changeTrack])
  const nextTrack = useCallback(() => changeTrack((trackIdxRef.current + 1) % PLAYLIST.length), [changeTrack])

  const genreCounts = useMemo(() => {
    const c = {}
    graphData.nodes.forEach(n => { c[n.genre] = (c[n.genre] || 0) + 1 })
    return Object.entries(c).sort((a, b) => b[1] - a[1])
  }, [])

  const filteredGenres = genreSearch
    ? genreCounts.filter(([g]) => g.includes(genreSearch.toLowerCase()))
    : genreCounts

  return (
    <aside className={styles.sidebar}>
      <a className={styles.backLink} href="../">
        ← Escolher parte
      </a>

      <div className={styles.brand}>
        <div className={styles.brandIcon}>
          <span /><span /><span />
        </div>
        <div className={styles.brandText}>SPOTIFY<br />GRAPHS</div>
      </div>

      <nav className={styles.nav}>
        {NAV_ITEMS.map(item => (
          <div
            key={item.label}
            className={`${styles.navItem} ${page === item.id ? styles.active : ''}`}
            onClick={() => item.id && setPage(item.id)}
          >
            <span className={styles.navIcon}>{item.icon}</span>
            {item.label}
          </div>
        ))}
      </nav>

      {page === 'explore' && (
        <div className={styles.filters}>

          <div className={styles.filterLabel}>Filtrar por gênero</div>
          <input
            className={styles.searchBox}
            placeholder="Gênero…"
            value={genreSearch}
            onChange={e => setGenreSearch(e.target.value)}
          />
          <div className={styles.genreList}>
            <div
              className={`${styles.genreItem} ${!activeGenre ? styles.genreSelected : ''}`}
              onClick={() => setActiveGenre(null)}
            >
              <span className={styles.gdot} style={{ background: '#fff' }} />
              <span>Todos</span>
              <span className={styles.gcount}>{graphData.nodes.length}</span>
            </div>
            {filteredGenres.map(([genre, count]) => (
              <div
                key={genre}
                className={`${styles.genreItem} ${activeGenre === genre ? styles.genreSelected : ''}`}
                onClick={() => setActiveGenre(genre)}
              >
                <span className={styles.gdot} style={{ background: genreColor(genre) }} />
                <span>{genre}</span>
                <span className={styles.gcount}>{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className={styles.player}>
        <div className={styles.playerHeader}>
          <button className={styles.pcBtn} onClick={prevTrack} title="Anterior">⏮</button>
          <div className={styles.playerInfo}>
            <div className={styles.playerName}>{PLAYLIST[trackIdx].name}</div>
            <div className={styles.playerArtist}>{PLAYLIST[trackIdx].artist}</div>
          </div>
          <button className={styles.pcBtn} onClick={nextTrack} title="Próxima">⏭</button>
        </div>
        <div ref={containerRef} className={styles.spotifyEmbed} />
        <div className={styles.trackDots}>
          {PLAYLIST.map((_, i) => (
            <span
              key={i}
              className={`${styles.dot} ${i === trackIdx ? styles.dotActive : ''}`}
              onClick={() => changeTrack(i)}
            />
          ))}
        </div>
      </div>
    </aside>
  )
}
