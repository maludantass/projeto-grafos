import { useState, useRef, useEffect, useMemo } from 'react'
import graphData from '../data/graph.json'
import { genreColor } from '../utils/genreColor'
import styles from './SearchBar.module.css'

export default function SearchBar({ onFocusNode }) {
  const [query, setQuery]       = useState('')
  const [open, setOpen]         = useState(false)
  const wrapRef                 = useRef(null)

  const results = useMemo(() => {
    if (!query.trim()) return []
    const q = query.toLowerCase()
    return graphData.nodes
      .filter(n => n.name.toLowerCase().includes(q) || n.artist.toLowerCase().includes(q))
      .slice(0, 8)
  }, [query])

  useEffect(() => {
    function onClickOutside(e) {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', onClickOutside)
    return () => document.removeEventListener('mousedown', onClickOutside)
  }, [])

  function handleSelect(node) {
    setQuery(node.name)
    setOpen(false)
    onFocusNode?.(node)
  }

  const showDropdown = open && query.trim().length > 0

  return (
    <div className={styles.wrap} ref={wrapRef}>
      <div className={`${styles.bar} ${showDropdown ? styles.barOpen : ''}`}>
        <span className={styles.icon}>🔍</span>
        <input
          className={styles.input}
          placeholder="Buscar música ou artista…"
          value={query}
          onChange={e => { setQuery(e.target.value); setOpen(true) }}
          onFocus={() => setOpen(true)}
        />
        {query && (
          <button className={styles.clear} onClick={() => { setQuery(''); setOpen(false) }}>
            ✕
          </button>
        )}
      </div>

      {showDropdown && (
        <div className={styles.dropdown}>
          {results.length === 0 ? (
            <div className={styles.empty}>Nenhum resultado encontrado</div>
          ) : results.map(node => (
            <div key={node.id} className={styles.item} onMouseDown={() => handleSelect(node)}>
              <span className={styles.dot} style={{ background: genreColor(node.genre) }} />
              <div className={styles.info}>
                <div className={styles.name}>{node.name}</div>
                <div className={styles.sub}>{node.artist} · <span style={{ color: genreColor(node.genre) }}>{node.genre}</span></div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
