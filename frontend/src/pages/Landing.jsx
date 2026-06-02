import { useEffect, useRef, useMemo } from 'react'
import { genreColor } from '../utils/genreColor'
import graphData from '../data/graph.json'
import styles from './Landing.module.css'

const FEATURED = [
  { artist: 'Farruko',       rx: 0.70, ry: 0.22, color: '#00e676' },
  { artist: 'Eagles',        rx: 0.52, ry: 0.35, color: '#ffffff' },
  { artist: "Guns N' Roses", rx: 0.78, ry: 0.38, color: '#d500f9' },
  { artist: 'Labrinth',      rx: 0.36, ry: 0.30, color: '#00e676' },
  { artist: 'Charlie Puth',  rx: 0.44, ry: 0.57, color: '#d500f9' },
  { artist: 'The 1975',      rx: 0.60, ry: 0.63, color: '#9c27b0' },
  { artist: 'The Beatles',   rx: 0.74, ry: 0.60, color: '#d500f9' },
]

export default function Landing({ setPage }) {
  const stats = useMemo(() => {
    const totalMusicas = graphData.nodes.length
    const totalGeneros = new Set(graphData.nodes.map(n => n.genre)).size
    const totalConexoes = graphData.edges.length
    return [
      [totalMusicas.toLocaleString('pt-BR'), 'Músicas'],
      [totalGeneros.toString(), 'Gêneros'],
      [totalConexoes.toLocaleString('pt-BR'), 'Conexões'],
      ['∞', 'Possibilidades'],
    ]
  }, [])

  const canvasRef  = useRef(null)
  const rafRef     = useRef(null)
  const stateRef   = useRef({ bg: [], feat: [], W: 0, H: 0 })
  const tooltipRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    const ctx    = canvas.getContext('2d')
    const s      = stateRef.current

    function resize() {
      s.W = canvas.width  = canvas.offsetWidth
      s.H = canvas.height = canvas.offsetHeight
      initNodes()
    }

    function initNodes() {
      s.bg = Array.from({ length: 400 }, (_, i) => {
        const side = i < 200 ? 0 : 1
        return {
          x:  side === 0 ? Math.random() * s.W * .65 : Math.random() * s.W * .65 + s.W * .35,
          y:  side === 0 ? Math.random() * s.H * .60 : Math.random() * s.H * .60 + s.H * .40,
          vx: (Math.random() - .5) * .22,
          vy: (Math.random() - .5) * .22,
          r:  Math.random() * 2 + 1,
          color: side === 0 ? '#00e676' : '#d500f9',
          alpha: Math.random() * .4 + .2,
        }
      })
      s.feat = FEATURED.map(d => ({
        ...d, x: d.rx * s.W, y: d.ry * s.H,
        vx: (Math.random() - .5) * .1, vy: (Math.random() - .5) * .1,
        r: 28, pulse: Math.random() * Math.PI * 2,
      }))
    }

    function draw() {
      ctx.clearRect(0, 0, s.W, s.H)

      for (const n of s.bg) {
        n.x += n.vx; n.y += n.vy
        if (n.x < 0 || n.x > s.W) n.vx *= -1
        if (n.y < 0 || n.y > s.H) n.vy *= -1
      }

      for (let i = 0; i < s.bg.length; i++) {
        for (let j = i + 1; j < s.bg.length; j++) {
          const a = s.bg[i], b = s.bg[j]
          const dx = a.x - b.x, dy = a.y - b.y
          const d  = dx*dx + dy*dy
          if (d > 14400) continue
          const dist = Math.sqrt(d)
          const alpha = (1 - dist / 120) * .18
          ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y)
          ctx.strokeStyle = a.color === b.color
            ? (a.color === '#00e676' ? `rgba(0,230,118,${alpha})` : `rgba(213,0,249,${alpha})`)
            : `rgba(41,121,255,${alpha * .5})`
          ctx.lineWidth = .6; ctx.stroke()
        }
      }

      for (const n of s.bg) {
        ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, Math.PI*2)
        ctx.fillStyle = n.color === '#00e676' ? `rgba(0,230,118,${n.alpha})` : `rgba(213,0,249,${n.alpha})`
        ctx.fill()
      }

      for (const n of s.feat) {
        n.x += n.vx; n.y += n.vy; n.pulse += .025
        if (n.x < n.r || n.x > s.W - n.r) n.vx *= -1
        if (n.y < n.r || n.y > s.H - n.r) n.vy *= -1

        const pr = n.r + 10 + Math.sin(n.pulse) * 4
        for (const b of s.bg) {
          const dx = n.x - b.x, dy = n.y - b.y, d = Math.sqrt(dx*dx + dy*dy)
          if (d > 140) continue
          ctx.beginPath(); ctx.moveTo(n.x, n.y); ctx.lineTo(b.x, b.y)
          ctx.strokeStyle = `rgba(255,255,255,${(1-d/140)*.08})`; ctx.lineWidth = .5; ctx.stroke()
        }

        const grd = ctx.createRadialGradient(n.x, n.y, n.r, n.x, n.y, pr + 8)
        grd.addColorStop(0, n.color + '44'); grd.addColorStop(1, n.color + '00')
        ctx.beginPath(); ctx.arc(n.x, n.y, pr + 8, 0, Math.PI*2); ctx.fillStyle = grd; ctx.fill()

        ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, Math.PI*2)
        ctx.fillStyle = n.color === '#ffffff' ? 'rgba(255,255,255,.12)' : n.color + '22'
        ctx.fill()
        ctx.strokeStyle = n.color; ctx.lineWidth = 1.5
        ctx.shadowBlur = 12; ctx.shadowColor = n.color; ctx.stroke(); ctx.shadowBlur = 0

        ctx.fillStyle = '#fff'; ctx.font = 'bold 10px system-ui'; ctx.textAlign = 'center'
        ctx.fillText(n.artist.toUpperCase(), n.x, n.y + n.r + 14)
      }

      rafRef.current = requestAnimationFrame(draw)
    }

    window.addEventListener('resize', resize)
    resize()
    rafRef.current = requestAnimationFrame(draw)
    return () => { cancelAnimationFrame(rafRef.current); window.removeEventListener('resize', resize) }
  }, [])

  function onMouseMove(e) {
    const canvas = canvasRef.current
    const rect   = canvas.getBoundingClientRect()
    const mx = e.clientX - rect.left
    const my = e.clientY - rect.top
    const tt = tooltipRef.current
    const s  = stateRef.current

    const hit = s.feat.find(n => {
      const dx = mx - n.x, dy = my - n.y
      return Math.sqrt(dx*dx + dy*dy) <= n.r + 8
    })

    if (!hit) { tt.style.display = 'none'; e.currentTarget.style.cursor = 'default'; return }
    e.currentTarget.style.cursor = 'pointer'

    tt.querySelector('[data-artist]').textContent = hit.artist
    tt.querySelector('[data-genre]').style.color  = hit.color

    const W = e.currentTarget.offsetWidth
    let tx = hit.x + hit.r + 16
    if (tx + 180 > W - 20) tx = hit.x - hit.r - 196
    tt.style.left    = tx + 'px'
    tt.style.top     = (hit.y - 30) + 'px'
    tt.style.display = 'flex'
    tt.style.borderColor = hit.color + '44'
  }

  function onMouseLeave() {
    if (tooltipRef.current) tooltipRef.current.style.display = 'none'
  }

  return (
    <div className={styles.page} onMouseMove={onMouseMove} onMouseLeave={onMouseLeave}>
      <canvas ref={canvasRef} className={styles.canvas} />

      {/* tooltip */}
      <div ref={tooltipRef} className={styles.tooltip} style={{ display: 'none' }}>
        <span data-artist className={styles.ttArtist} />
        <span data-genre  className={styles.ttGenre}>▲ artista em destaque</span>
      </div>

      <div className={styles.overlay}>
        <span className={styles.badge}>PARTE 2</span>
        <h1 className={styles.title}>
          CONECTANDO <span className={styles.g}>SONS.</span><br />
          EXPLORANDO<br />
          <span className={styles.p}>INFINITOS.</span>
        </h1>
        <p className={styles.sub}>
          Um mergulho na rede de músicas do Spotify
          usando grafos e algoritmos para descobrir
          padrões, conexões e novas experiências musicais.
        </p>
        <button className={styles.cta} onClick={() => setPage('explore')}>
          EXPLORAR REDE &nbsp;→
        </button>
        <div className={styles.scroll}>
          <div className={styles.scrollIcon} />
          ROLE PARA BAIXO
        </div>
      </div>

      <div className={styles.hint}>
        <span>↖</span> PASSE O MOUSE SOBRE OS NÓS PARA VER DETALHES
      </div>

      <div className={styles.statsBar}>
        {stats.map(([v, l]) => (
          <div key={l} className={styles.statBlock}>
            <div className={styles.statVal}>{v}</div>
            <div className={styles.statLbl}>{l}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
