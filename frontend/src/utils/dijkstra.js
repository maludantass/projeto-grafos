class MinHeap {
  constructor() { this.h = [] }

  push(dist, id) {
    this.h.push([dist, id])
    this._up(this.h.length - 1)
  }

  pop() {
    const top = this.h[0]
    const last = this.h.pop()
    if (this.h.length > 0) { this.h[0] = last; this._down(0) }
    return top
  }

  get size() { return this.h.length }

  _up(i) {
    while (i > 0) {
      const p = (i - 1) >> 1
      if (this.h[p][0] <= this.h[i][0]) break
      ;[this.h[p], this.h[i]] = [this.h[i], this.h[p]]
      i = p
    }
  }

  _down(i) {
    const n = this.h.length
    while (true) {
      let m = i, l = 2*i+1, r = 2*i+2
      if (l < n && this.h[l][0] < this.h[m][0]) m = l
      if (r < n && this.h[r][0] < this.h[m][0]) m = r
      if (m === i) break
      ;[this.h[m], this.h[i]] = [this.h[i], this.h[m]]
      i = m
    }
  }
}

export function runDijkstra(nodes, links, sourceId) {
  // monta lista de adjacência a partir dos dados do react-force-graph
  const adj = new Map()
  nodes.forEach(n => adj.set(n.id, []))

  links.forEach(e => {
    const s = typeof e.source === 'object' ? e.source.id : e.source
    const t = typeof e.target === 'object' ? e.target.id : e.target
    // peso = distância euclidiana = 1 - similaridade
    const w = Math.max(0, 1 - (e.value ?? 0))
    adj.get(s)?.push({ to: t, w })
    adj.get(t)?.push({ to: s, w })
  })

  const dist = new Map()
  const prev = new Map()
  nodes.forEach(n => { dist.set(n.id, Infinity); prev.set(n.id, null) })
  dist.set(sourceId, 0)

  const heap = new MinHeap()
  heap.push(0, sourceId)
  const visited = new Set()

  while (heap.size > 0) {
    const [d, u] = heap.pop()
    if (visited.has(u)) continue
    visited.add(u)
    for (const { to, w } of (adj.get(u) || [])) {
      const nd = d + w
      if (nd < dist.get(to)) {
        dist.set(to, nd)
        prev.set(to, u)
        heap.push(nd, to)
      }
    }
  }

  return { dist, prev }
}

export function reconstructPath(prev, sourceId, targetId) {
  const path = []
  let cur = targetId
  while (cur !== null && cur !== undefined) {
    path.unshift(cur)
    if (cur === sourceId) break
    cur = prev.get(cur)
  }
  return path[0] === sourceId ? path : null
}
