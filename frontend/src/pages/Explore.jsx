import { useMemo, useRef, useEffect, useCallback, useState } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import graphData from '../data/graph.json'
import { genreColor } from '../utils/genreColor'
import { runDijkstra, reconstructPath } from '../utils/dijkstra'
import SearchBar from '../components/SearchBar'
import styles from './Explore.module.css'

export default function Explore({
  activeGenre, strength, setSelectedNode, pathMode, setPathMode,
}) {
  const graphRef = useRef()
  const dataRef  = useRef(null)   // keeps current graph data accessible in callbacks

  const [highlightId, setHighlightId] = useState(null)
  const [pathSource, setPathSource]   = useState(null)
  const [pathResult, setPathResult]   = useState(null)   // { path, dist } | { notFound }

  const pathNodeSet = useMemo(() => new Set(pathResult?.path ?? []), [pathResult])
  const pathEdgeSet = useMemo(() => {
    if (!pathResult) return new Set()
    const s = new Set()
    for (let i = 0; i < pathResult.path.length - 1; i++) {
      s.add(`${pathResult.path[i]}|${pathResult.path[i + 1]}`)
      s.add(`${pathResult.path[i + 1]}|${pathResult.path[i]}`)
    }
    return s
  }, [pathResult])

  // Pré-computa componentes conexas uma única vez (BFS no grafo completo)
  const componentMap = useMemo(() => {
    const adj = new Map()
    graphData.nodes.forEach(n => adj.set(n.id, []))
    graphData.edges.forEach(e => {
      adj.get(e.source)?.push(e.target)
      adj.get(e.target)?.push(e.source)
    })
    const comp = new Map()
    let compId = 0
    for (const node of graphData.nodes) {
      if (comp.has(node.id)) continue
      const queue = [node.id]
      let qi = 0
      comp.set(node.id, compId)
      while (qi < queue.length) {
        const u = queue[qi++]
        for (const v of (adj.get(u) || [])) {
          if (!comp.has(v)) { comp.set(v, compId); queue.push(v) }
        }
      }
      compId++
    }
    return comp
  }, [])

  // stable refs for draw callbacks — prevent simulation restarts on state changes
  const highlightIdRef   = useRef(highlightId)
  const pathNodeSetRef   = useRef(pathNodeSet)
  const pathEdgeSetRef   = useRef(pathEdgeSet)
  const pathSourceRef    = useRef(pathSource)
  const pathResultRef    = useRef(pathResult)
  const componentMapRef  = useRef(componentMap)
  useEffect(() => { highlightIdRef.current  = highlightId   }, [highlightId])
  useEffect(() => { pathNodeSetRef.current  = pathNodeSet   }, [pathNodeSet])
  useEffect(() => { pathEdgeSetRef.current  = pathEdgeSet   }, [pathEdgeSet])
  useEffect(() => { pathSourceRef.current   = pathSource    }, [pathSource])
  useEffect(() => { pathResultRef.current   = pathResult    }, [pathResult])
  useEffect(() => { componentMapRef.current = componentMap  }, [componentMap])

  const threshold = strength / 100

  const data = useMemo(() => {
    const nodes = activeGenre
      ? graphData.nodes.filter(n => n.genre === activeGenre)
      : graphData.nodes
    const ids = new Set(nodes.map(n => n.id))
    const links = graphData.edges
      .filter(e => e.value >= threshold && ids.has(e.source) && ids.has(e.target))
      .map(e => ({ source: e.source, target: e.target, value: e.value }))

    const connectedIds = new Set()
    links.forEach(e => { connectedIds.add(e.source); connectedIds.add(e.target) })
    const visibleNodes = nodes.filter(n => connectedIds.has(n.id))

    return { nodes: visibleNodes.map(n => ({ ...n })), links }
  }, [activeGenre, threshold])

  // keep dataRef in sync so callbacks always read fresh node positions
  useEffect(() => { dataRef.current = data }, [data])

  // quando o caminho fica pronto, centraliza nos nós do caminho (força redraw + boa UX)
  useEffect(() => {
    if (!pathResult || pathResult.notFound) return
    const pathIds = new Set(pathResult.path)
    setTimeout(() => {
      graphRef.current?.zoomToFit(600, 80, n => pathIds.has(n.id))
    }, 50)
  }, [pathResult])

  // ── zoom to a node by id, retrying until the simulation places it ──
  const zoomToNode = useCallback((nodeId) => {
    const tryZoom = (attempts = 0) => {
      if (!graphRef.current || attempts > 30) return
      const node = (dataRef.current?.nodes ?? []).find(n => n.id === nodeId)
      if (node?.x != null && (node.x !== 0 || node.y !== 0)) {
        graphRef.current.centerAt(node.x, node.y, 700)
        setTimeout(() => graphRef.current?.zoom(4, 500), 200)
      } else {
        setTimeout(() => tryZoom(attempts + 1), 80)
      }
    }
    requestAnimationFrame(() => tryZoom())
  }, [])

  // ── search bar callback ──
  const handleFocusNode = useCallback((node) => {
    setSelectedNode(node)
    setHighlightId(node.id)
    zoomToNode(node.id)
  }, [setSelectedNode, zoomToNode])

  // ── draw each node ──
  const drawNode = useCallback((node, ctx) => {
    const r      = Math.sqrt(2 + node.degree * 0.6) * 4.5
    const color  = genreColor(node.genre)
    const isHL   = node.id === highlightIdRef.current
    const inPath = pathNodeSetRef.current.has(node.id)
    const pr     = pathResultRef.current
    const isSrc  = node.id === pathSourceRef.current?.id
    const isDst  = pr && node.id === pr.path[pr.path.length - 1]
    const dimmed = pr && !pr.notFound && !inPath && !isHL

    // Escurece nós em componente diferente da origem selecionada
    const srcId  = pathSourceRef.current?.id
    const unreachable = srcId && !pr &&
      componentMapRef.current.get(node.id) !== componentMapRef.current.get(srcId)

    if (dimmed)       ctx.globalAlpha = 0.1
    if (unreachable)  ctx.globalAlpha = 0.08

    if (isHL || inPath) {
      const zoom = graphRef.current?.zoom() ?? 1
      const haloExtra = Math.max(6, 10 / zoom)
      const ringExtra = Math.max(3, 5 / zoom)

      ctx.beginPath()
      ctx.arc(node.x, node.y, r + haloExtra, 0, Math.PI * 2)
      ctx.fillStyle = (isSrc ? '#00e676' : isDst ? '#ff2d78' : '#ffd700') + '33'
      ctx.fill()

      ctx.beginPath()
      ctx.arc(node.x, node.y, r + ringExtra, 0, Math.PI * 2)
      ctx.strokeStyle = isSrc ? '#00e676' : isDst ? '#ff2d78' : isHL ? '#fff' : '#ffd700'
      ctx.lineWidth = 1.5 / zoom
      ctx.stroke()
    }

    const nodeFill = isSrc ? '#00e676' : isDst ? '#ff2d78' : (isHL || inPath) ? '#fff' : color

    // glow suave com a cor do gênero (apenas nós normais visíveis)
    if (!dimmed && !isSrc && !isDst) {
      ctx.shadowColor = color
      ctx.shadowBlur  = r * 2.2
    }

    ctx.beginPath()
    ctx.arc(node.x, node.y, r, 0, Math.PI * 2)
    ctx.fillStyle = nodeFill
    ctx.fill()
    ctx.shadowBlur = 0

    if (isHL || inPath) {
      ctx.font = `bold ${Math.max(9, r + 1)}px system-ui`
      ctx.textAlign = 'center'
      ctx.fillStyle = '#fff'
      const label = node.name.length > 18 ? node.name.slice(0, 16) + '…' : node.name
      ctx.fillText(label, node.x, node.y + r + 11)
    }

    if (dimmed || unreachable) ctx.globalAlpha = 1
  }, [])

  // ── draw Dijkstra path overlay before nodes ──
  const handleRenderFramePre = useCallback((ctx) => {
    const pr = pathResultRef.current
    if (!pr || pr.notFound) return
    const nodes = dataRef.current?.nodes ?? []
    const nodeMap = new Map(nodes.map(n => [n.id, n]))

    // divide pelo zoom para manter espessura constante em pixels de tela
    const zoom = graphRef.current?.zoom() ?? 1

    ctx.save()
    ctx.strokeStyle = '#ffd700'
    ctx.lineWidth = 4 / zoom
    ctx.shadowColor = '#ffd700'
    ctx.shadowBlur = 12 / zoom
    for (let i = 0; i < pr.path.length - 1; i++) {
      const a = nodeMap.get(pr.path[i])
      const b = nodeMap.get(pr.path[i + 1])
      if (!a || !b || a.x == null || b.x == null) continue
      ctx.beginPath()
      ctx.moveTo(a.x, a.y)
      ctx.lineTo(b.x, b.y)
      ctx.stroke()
    }
    ctx.restore()
  }, [])

  // ── node click: normal selection or Dijkstra path building ──
  const handleNodeClick = useCallback((node) => {
    if (!pathMode) {
      setSelectedNode(node)
      setHighlightId(node.id)
      graphRef.current?.centerAt(node.x, node.y, 600)
      setTimeout(() => graphRef.current?.zoom(4, 500), 200)
      return
    }

    if (!pathSource) {
      setPathSource(node)
      setPathResult(null)
      return
    }
    if (node.id === pathSource.id) return

    // Verifica componente antes de rodar Dijkstra
    const srcComp = componentMap.get(pathSource.id)
    const dstComp = componentMap.get(node.id)
    if (srcComp !== dstComp) {
      setPathResult({ path: [pathSource.id, node.id], dist: Infinity, notFound: true, differentComponent: true })
      setSelectedNode(node)
      return
    }

    // run Dijkstra on the full graph (ignores active genre / strength filters)
    const { dist, prev } = runDijkstra(
      graphData.nodes,
      graphData.edges.map(e => ({ source: e.source, target: e.target, value: e.value })),
      pathSource.id,
    )
    const path = reconstructPath(prev, pathSource.id, node.id)
    setPathResult(path
      ? { path, dist: dist.get(node.id) }
      : { path: [pathSource.id, node.id], dist: Infinity, notFound: true, differentComponent: false }
    )
    setSelectedNode(node)
  }, [pathMode, pathSource, setSelectedNode])

  function clearPath() {
    setPathSource(null)
    setPathResult(null)
  }

  function clearSelection() {
    setHighlightId(null)
    setSelectedNode(null)
  }

  const stepLabel = !pathSource
    ? '1. Clique na música de origem'
    : !pathResult
      ? '2. Clique na música de destino'
      : null

  const destNode = pathResult
    ? graphData.nodes.find(n => n.id === pathResult.path[pathResult.path.length - 1])
    : null

  return (
    <div style={{ width: '100%', height: '100%', background: '#06060f', position: 'relative' }}>
      <SearchBar onFocusNode={handleFocusNode} />

      {highlightId && !pathMode && (
        <button
          onClick={clearSelection}
          style={{
            position: 'absolute', top: 12, right: 12, zIndex: 20,
            background: 'rgba(30,30,50,0.9)', border: '1px solid rgba(255,255,255,0.2)',
            color: '#fff', borderRadius: 6, padding: '5px 14px', cursor: 'pointer', fontSize: '0.78rem',
          }}
        >
          ✕ limpar seleção
        </button>
      )}

      {pathMode && (
        <div className={styles.pathPanel}>
          {stepLabel && <span className={styles.pathStep}>{stepLabel}</span>}

          {pathSource && !pathResult && (
            <>
              <span className={styles.pathNode} style={{ color: '#00e676' }}>
                ● {pathSource.name}
              </span>
              <span style={{ fontSize: '.72rem', color: 'rgba(255,255,255,0.3)' }}>
                nós escuros = componente diferente (sem caminho)
              </span>
            </>
          )}

          {pathResult && !pathResult.notFound && (
            <>
              <span className={styles.pathNode} style={{ color: '#00e676' }}>
                ● {pathSource.name}
              </span>
              <span className={styles.pathArrow}>→</span>
              <span className={styles.pathNode} style={{ color: '#ff2d78' }}>
                ● {destNode?.name}
              </span>
              <span className={styles.pathMeta}>
                {pathResult.path.length - 1} saltos · dist {pathResult.dist.toFixed(3)}
              </span>
            </>
          )}

          {pathResult?.notFound && (
            <span style={{ color: '#ff6d00', fontSize: '.78rem' }}>
              {pathResult.differentComponent
                ? '⚠ Componentes desconexos — nenhum caminho possível'
                : 'Caminho não encontrado'}
            </span>
          )}

          {(pathSource || pathResult) && (
            <button className={styles.clearBtn} onClick={clearPath}>✕ limpar</button>
          )}
        </div>
      )}

      <ForceGraph2D
        ref={graphRef}
        graphData={data}
        backgroundColor="#06060f"
        nodeCanvasObject={drawNode}
        nodeCanvasObjectMode={() => 'replace'}
        linkColor={link => {
          const pr = pathResultRef.current
          const s = typeof link.source === 'object' ? link.source.id : link.source
          const t = typeof link.target === 'object' ? link.target.id : link.target
          if (pr && !pr.notFound) {
            return pathEdgeSetRef.current.has(`${s}|${t}`)
              ? 'rgba(255,215,0,0.9)'
              : 'rgba(255,255,255,0.04)'
          }
          // cor da aresta = cor do gênero do nó de origem (com opacidade baixa)
          const genre = typeof link.source === 'object' ? link.source.genre : null
          return genreColor(genre ?? '') + '50'  // ~31% opacidade
        }}
        linkWidth={link => {
          const pr = pathResultRef.current
          if (!pr || pr.notFound) return 1.0
          const s = typeof link.source === 'object' ? link.source.id : link.source
          const t = typeof link.target === 'object' ? link.target.id : link.target
          return pathEdgeSetRef.current.has(`${s}|${t}`) ? 2.5 : 0.5
        }}
        onNodeClick={handleNodeClick}
        onRenderFramePre={handleRenderFramePre}
        nodeLabel={n => `${n.name} — ${n.artist} (${n.genre})`}
        warmupTicks={100}
        cooldownTime={10000}
        d3AlphaDecay={0.05}
        d3VelocityDecay={0.45}
      />
    </div>
  )
}
