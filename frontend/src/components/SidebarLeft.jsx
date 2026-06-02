import { useMemo, useState } from 'react'
import graphData from '../data/graph.json'
import { genreColor } from '../utils/genreColor'
import styles from './SidebarLeft.module.css'

const NAV_ITEMS = [
  { id: 'landing', icon: '⌂', label: 'INÍCIO' },
  { id: 'explore', icon: '⚡', label: 'EXPLORAR REDE' },
  { id: null,      icon: '⌨', label: 'ALGORITMOS' },
  { id: null,      icon: '▦', label: 'VISUALIZAÇÕES' },
  { id: null,      icon: '⬡', label: 'PLAYLIST LAB' },
  { id: null,      icon: 'ℹ', label: 'SOBRE O PROJETO' },
]

export default function SidebarLeft({ page, setPage, activeGenre, setActiveGenre }) {
  const [genreSearch, setGenreSearch] = useState('')

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
        <div className={styles.playerTrack}>
          <div className={styles.playerArt}>🎵</div>
          <div className={styles.playerInfo}>
            <div className={styles.playerName}>Time</div>
            <div className={styles.playerArtist}>Pink Floyd</div>
          </div>
          <span style={{ color: 'var(--pink)', fontSize: 12 }}>♥</span>
        </div>
        <div className={styles.playerControls}>
          <button className={styles.pcBtn}>⏮</button>
          <button className={styles.pcPlay}>▶</button>
          <button className={styles.pcBtn}>⏭</button>
        </div>
        <div className={styles.playerBar}>
          <div className={styles.playerProg} />
        </div>
      </div>
    </aside>
  )
}
