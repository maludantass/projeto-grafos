import { useMemo, useState, useEffect } from 'react'
import reportData from '../../../out/parte2_report.json'
import styles from './Benchmark.module.css'

/* ─── Paleta de cores ─────────────────────────────────────────────────────── */
const COLORS = {
  'BFS':                              '#00e676',
  'DFS':                              '#d500f9',
  'Dijkstra':                         '#ffd700',
  'Bellman-Ford':                     '#ff2d78',
  'Carregamento do grafo':            '#4fc3f7',
  'Componentes Conexos (DFS global)': '#ff9800',
}

const ALGO_GROUPS = [
  { key: 'Carregamento',  label: 'Carregamento',  color: '#4fc3f7' },
  { key: 'BFS',           label: 'BFS',           color: '#00e676' },
  { key: 'DFS',           label: 'DFS',           color: '#d500f9' },
  { key: 'Dijkstra',      label: 'Dijkstra',      color: '#ffd700' },
  { key: 'Bellman-Ford',  label: 'Bellman-Ford',  color: '#ff2d78' },
  { key: 'Componentes',   label: 'Componentes',   color: '#ff9800' },
]

function getAlgoKey(tarefa) {
  if (tarefa.startsWith('Carregamento')) return 'Carregamento'
  if (tarefa.startsWith('BFS'))         return 'BFS'
  if (tarefa.startsWith('DFS fonte'))   return 'DFS'
  if (tarefa.startsWith('Dijkstra'))    return 'Dijkstra'
  if (tarefa.startsWith('Bellman'))     return 'Bellman-Ford'
  if (tarefa.startsWith('Componentes')) return 'Componentes'
  return null
}

function algoColor(nome) {
  // check longer keys first to avoid 'DFS' matching 'Componentes Conexos (DFS global)'
  const sorted = Object.entries(COLORS).sort((a, b) => b[0].length - a[0].length)
  for (const [k, v] of sorted) {
    if (nome.includes(k)) return v
  }
  return '#888'
}

function shortLabel(tarefa) {
  return tarefa
    .replace(' (Busca em Largura)', '')
    .replace(' (Busca em Profundidade)', '')
    .replace(' (caminho mínimo, single-source)', '')
    .replace(' (DFS global)', '')
    .replace(' — Seu Zé Que Ta Chegando - Ao Vivo (brazil)', ' (f.1)')
    .replace(' — Eleanor - Edit (pop)', ' (f.2)')
    .replace(" — Gangsta's Paradise (funk)", ' (f.3)')
}

function heatColor(norm) {
  const hue = Math.round((1 - Math.min(norm, 1)) * 118)
  return `hsl(${hue}, 82%, 40%)`
}

/* ─── Legenda descritiva ─────────────────────────────────────────────────── */
function ExplainedLegend({ items, note }) {
  return (
    <div className={styles.legendExplained}>
      {items.map(it => (
        <div key={it.label} className={styles.legendExplainedRow}>
          <span className={styles.legendExplainedDot}
            style={{ background: it.color, borderRadius: it.square ? 3 : '50%' }} />
          <div>
            <span style={{ color: it.color, fontWeight: 700, marginRight: 6 }}>{it.label}</span>
            <span className={styles.legendExplainedDesc}>{it.desc}</span>
          </div>
        </div>
      ))}
      {note && <div className={styles.legendNote}>{note}</div>}
    </div>
  )
}

/* ═══════════════════════════════════════════════════════════════════════════
   GRÁFICO 1 — Dispersão: Memória × Tempo
   ═══════════════════════════════════════════════════════════════════════════ */
function ScatterChart({ medicoes, activeAlgos }) {
  const [hov, setHov] = useState(null)
  const W = 900, H = 420
  const PL = 80, PR = 40, PT = 30, PB = 60
  const iW = W - PL - PR, iH = H - PT - PB

  const logMin = Math.log10(5), logMax = Math.log10(1300)
  const xS = v => PL + ((Math.log10(v) - logMin) / (logMax - logMin)) * iW
  const yLogMin = Math.log10(150), yLogMax = Math.log10(35000)
  const yS = v => PT + iH - ((Math.log10(v) - yLogMin) / (yLogMax - yLogMin)) * iH
  const xTicks = [5, 10, 20, 50, 100, 200, 500, 1000]
  const yTicks = [200, 500, 1000, 2000, 5000, 10000, 25000]
  // spread overlapping dots in same algo group using circular jitter
  const algoGroups = {}
  medicoes.forEach(m => {
    const k = getAlgoKey(m.tarefa) ?? m.tarefa
    if (!algoGroups[k]) algoGroups[k] = []
    algoGroups[k].push(m)
  })
  const algoIdx = {}
  const SPREAD_R = 18
  const pts = medicoes.map(m => {
    const k = getAlgoKey(m.tarefa) ?? m.tarefa
    const n = algoGroups[k].length
    const i = algoIdx[k] = (algoIdx[k] ?? 0)
    algoIdx[k]++
    const cx0 = xS(m.tempo_medio_ms), cy0 = yS(m.memoria_pico_kb)
    if (n <= 1) return { ...m, cx: cx0, cy: cy0 }
    const angle = (i / n) * 2 * Math.PI - Math.PI / 2
    return { ...m, cx: cx0 + SPREAD_R * Math.cos(angle), cy: cy0 + SPREAD_R * Math.sin(angle) }
  })

  return (
    <>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{ overflow: 'visible' }}>
        {/* zona ideal */}
        <rect x={PL} y={yS(1050)} width={xS(28) - PL} height={PT + iH - yS(1050)}
          fill="rgba(0,230,118,0.05)" rx={6} />
        <text x={PL + 8} y={yS(1050) + 18} fill="rgba(0,230,118,0.3)" fontSize={10} fontStyle="italic">
          zona ideal ↙
        </text>
        {/* grid */}
        {yTicks.map(t => <line key={t} x1={PL} x2={W-PR} y1={yS(t)} y2={yS(t)} stroke="rgba(255,255,255,0.06)" strokeWidth={1}/>)}
        {xTicks.map(t => <line key={t} x1={xS(t)} x2={xS(t)} y1={PT} y2={PT+iH} stroke="rgba(255,255,255,0.06)" strokeWidth={1}/>)}
        {/* eixos */}
        <line x1={PL} x2={W-PR} y1={PT+iH} y2={PT+iH} stroke="rgba(255,255,255,0.22)" strokeWidth={1}/>
        <line x1={PL} x2={PL} y1={PT} y2={PT+iH} stroke="rgba(255,255,255,0.22)" strokeWidth={1}/>
        {xTicks.map(t => (
          <text key={t} x={xS(t)} y={PT+iH+20} textAnchor="middle" fill="rgba(255,255,255,0.42)" fontSize={11}>{t} ms</text>
        ))}
        {yTicks.map(t => (
          <text key={t} x={PL-8} y={yS(t)+4} textAnchor="end" fill="rgba(255,255,255,0.42)" fontSize={11}>
            {t >= 1000 ? `${t/1000}k` : t}
          </text>
        ))}
        <text x={PL+iW/2} y={H-8} textAnchor="middle" fill="rgba(255,255,255,0.45)" fontSize={12} fontWeight="600">
          Tempo médio de execução (ms) — escala logarítmica →
        </text>
        <text x={18} y={PT+iH/2} textAnchor="middle" fill="rgba(255,255,255,0.45)" fontSize={12} fontWeight="600"
          transform={`rotate(-90,18,${PT+iH/2})`}>↑ Memória pico (KB) — escala log</text>
        {/* pontos */}
        {pts.map(p => {
          const key    = getAlgoKey(p.tarefa)
          const active = !key || activeAlgos.has(key)
          const color  = algoColor(p.tarefa)
          const isHov  = hov === p.tarefa
          const tipX   = p.cx > W*0.6 ? p.cx-214 : p.cx+18
          const tipY   = Math.max(PT+4, p.cy > H*0.65 ? p.cy-104 : p.cy-14)
          return (
            <g key={p.tarefa} onMouseEnter={()=>setHov(p.tarefa)} onMouseLeave={()=>setHov(null)} style={{cursor:'pointer'}}>
              <circle cx={p.cx} cy={p.cy} r={isHov?13:9}
                fill={active?color:'#555'} fillOpacity={active?(isHov?1:0.82):0.2}
                stroke={isHov?'#fff':'transparent'} strokeWidth={2}
                style={{transition:'r 0.15s,fill-opacity 0.22s,fill 0.22s'}}/>
              {isHov && (
                <>
                  <rect x={tipX} y={tipY} width={208} height={104} rx={8}
                    fill="rgba(5,5,18,0.97)" stroke={`${color}55`} strokeWidth={1.5}/>
                  <text x={tipX+14} y={tipY+22} fill={color} fontSize={12} fontWeight="bold">{shortLabel(p.tarefa)}</text>
                  <text x={tipX+14} y={tipY+42} fill="rgba(255,255,255,0.75)" fontSize={11}>⏱ Médio: {p.tempo_medio_ms.toFixed(2)} ms</text>
                  <text x={tipX+14} y={tipY+59} fill="rgba(255,255,255,0.65)" fontSize={11}>⏱ Mínimo: {p.tempo_min_ms.toFixed(2)} ms</text>
                  <text x={tipX+14} y={tipY+76} fill="rgba(255,255,255,0.75)" fontSize={11}>💾 Memória: {p.memoria_pico_kb.toFixed(0)} KB</text>
                  <text x={tipX+14} y={tipY+96} fill="rgba(255,255,255,0.38)" fontSize={9}>{p.complexidade_teorica}</text>
                </>
              )}
            </g>
          )
        })}
      </svg>
      <ExplainedLegend
        items={ALGO_GROUPS.map(g => ({ label: g.label, color: g.color, desc: '', dot: true }))}
        note="Leia o gráfico: quanto mais à esquerda = mais rápido; quanto mais abaixo = menos memória. A zona verde no canto inferior esquerdo representa o melhor custo-benefício. Ambos os eixos usam escala logarítmica — isso normaliza a distância euclidiana entre os pontos, trazendo o Carregamento (24k KB) para perto dos demais sem distorcer a comparação relativa."
      />
    </>
  )
}

/* ═══════════════════════════════════════════════════════════════════════════
   GRÁFICO 2 — BFS vs DFS por Fonte Musical
   ═══════════════════════════════════════════════════════════════════════════ */
function GroupedBarChart({ medicoes, activeAlgos }) {
  const [hov, setHov] = useState(null)
  const bfsRows = medicoes.filter(m => m.tarefa.startsWith('BFS fonte'))
  const dfsRows = medicoes.filter(m => m.tarefa.startsWith('DFS fonte'))
  const fontes  = [
    { label: 'Brazil (f.1)', short: 'Brazil', nos: bfsRows[0]?.nos_visitados },
    { label: 'Pop (f.2)',    short: 'Pop',    nos: bfsRows[1]?.nos_visitados },
    { label: 'Funk (f.3)',   short: 'Funk',   nos: bfsRows[2]?.nos_visitados },
  ]
  const maxVal = Math.max(...bfsRows.map(m=>m.tempo_medio_ms),...dfsRows.map(m=>m.tempo_medio_ms)) * 1.15

  const W=920, H=380, PL=50, PR=30, PT=40, PB=90
  const iW=W-PL-PR, iH=H-PT-PB
  const groupW=iW/3, barW=groupW*0.28, gap=groupW*0.06
  const yS = v => PT+iH-(v/maxVal)*iH
  const yTicks = [0,5,10,15,20,25]
  const bfsActive = activeAlgos.has('BFS')
  const dfsActive = activeAlgos.has('DFS')

  function barX(gi,bi){ return PL+gi*groupW+groupW/2-barW-gap/2+bi*(barW+gap) }

  return (
    <>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{overflow:'visible'}}>
        {yTicks.map(t=>(
          <g key={t}>
            <line x1={PL} x2={W-PR} y1={yS(t)} y2={yS(t)} stroke="rgba(255,255,255,0.07)" strokeWidth={1}/>
            <text x={PL-8} y={yS(t)+4} textAnchor="end" fill="rgba(255,255,255,0.38)" fontSize={11}>{t}</text>
          </g>
        ))}
        <line x1={PL} x2={W-PR} y1={PT+iH} y2={PT+iH} stroke="rgba(255,255,255,0.22)" strokeWidth={1}/>

        {fontes.map((fonte,gi)=>{
          const bfs=bfsRows[gi], dfs=dfsRows[gi]
          return [
            {m:bfs, color:COLORS['BFS'],  label:'BFS', bi:0, active:bfsActive},
            {m:dfs, color:COLORS['DFS'],  label:'DFS', bi:1, active:dfsActive},
          ].map(({m,color,label,bi,active})=>{
            if(!m) return null
            const x=barX(gi,bi), bH=(m.tempo_medio_ms/maxVal)*iH, y=PT+iH-bH
            const minY=PT+iH-(m.tempo_min_ms/maxVal)*iH
            const key=`${gi}-${label}`, isHov=hov===key
            return (
              <g key={key} onMouseEnter={()=>setHov(key)} onMouseLeave={()=>setHov(null)} style={{cursor:'pointer'}}>
                <rect x={x} y={y} width={barW} height={bH} rx={4}
                  fill={active?color:'#555'} fillOpacity={active?(isHov?1:0.68):0.18}
                  style={{transition:'fill-opacity 0.2s,fill 0.2s'}}/>
                {active && (
                  <line x1={x} x2={x+barW} y1={minY} y2={minY}
                    stroke={color} strokeWidth={2.5} strokeOpacity={0.55} strokeDasharray="4,3"/>
                )}
                {active && (
                  <text x={x+barW/2} y={y-7} textAnchor="middle" fill={color} fontSize={11} fontWeight="700" fillOpacity={0.85}>
                    {m.tempo_medio_ms.toFixed(1)}
                  </text>
                )}
                {isHov && active && (
                  <>
                    <rect x={x-8} y={y-76} width={164} height={68} rx={7}
                      fill="rgba(5,5,18,0.97)" stroke={`${color}55`} strokeWidth={1.5}/>
                    <text x={x} y={y-56} fill={color} fontSize={12} fontWeight="bold">{label} — {fonte.short}</text>
                    <text x={x} y={y-38} fill="rgba(255,255,255,0.75)" fontSize={11}>Médio: {m.tempo_medio_ms.toFixed(2)} ms</text>
                    <text x={x} y={y-22} fill="rgba(255,255,255,0.5)" fontSize={11}>Mínimo: {m.tempo_min_ms.toFixed(2)} ms</text>
                    <text x={x} y={y-8} fill="rgba(255,255,255,0.35)" fontSize={10}>Nós: {m.nos_visitados?.toLocaleString('pt-BR') ?? '—'}</text>
                  </>
                )}
              </g>
            )
          })
        })}

        {/* separadores de grupo */}
        {[1,2].map(i=>(
          <line key={i} x1={PL+i*groupW} x2={PL+i*groupW} y1={PT} y2={PT+iH}
            stroke="rgba(255,255,255,0.04)" strokeWidth={1} strokeDasharray="4,4"/>
        ))}

        {/* labels de grupo */}
        {fontes.map((f,gi)=>(
          <text key={gi} x={PL+gi*groupW+groupW/2} y={PT+iH+22} textAnchor="middle"
            fill="rgba(255,255,255,0.6)" fontSize={12} fontWeight="700">{f.label}</text>
        ))}

        {/* nota linha tracejada */}
        <line x1={PL+8} x2={PL+34} y1={PT+iH+54} y2={PT+iH+54}
          stroke="rgba(255,255,255,0.45)" strokeWidth={2.5} strokeDasharray="4,3"/>
        <text x={PL+42} y={PT+iH+58} fill="rgba(255,255,255,0.38)" fontSize={10}>
          linha tracejada = tempo mínimo atingido entre as 5 execuções
        </text>
        <text x={W/2} y={H-6} textAnchor="middle" fill="rgba(255,255,255,0.35)" fontSize={10}>
          Tempo (ms)
        </text>
      </svg>
      <ExplainedLegend
        items={[
          { label: 'BFS — Busca em Largura', color: COLORS['BFS'], desc: 'Usa fila (deque), visita nós nível por nível a partir da origem. Garante o menor número de saltos. Complexidade O(V+E).' },
          { label: 'DFS — Busca em Profundidade', color: COLORS['DFS'], desc: 'Usa recursão com coloração BRANCO/CINZA/PRETO. Percorre ramos completos antes de retroceder. Detecta ciclos e classifica arestas. Complexidade O(V+E).' },
        ]}
        note="Cada grupo de barras representa uma música-origem diferente. O objetivo é verificar se o desempenho é estável independente do ponto de partida — BFS mostrou variação de apenas ±0.9 ms entre as 3 fontes, enquanto DFS variou ±3.3 ms."
      />
    </>
  )
}

/* ═══════════════════════════════════════════════════════════════════════════
   GRÁFICO 3 — Mínimo vs Médio (escala log)
   ═══════════════════════════════════════════════════════════════════════════ */
function MinAvgChart({ medicoes, activeAlgos }) {
  const [hov, setHov] = useState(null)
  const rows = [
    { m: medicoes.find(m=>m.tarefa==='Carregamento do grafo'),    label:'Carregamento',  key:'Carregamento' },
    { m: medicoes.find(m=>m.tarefa.startsWith('BFS fonte 1')),    label:'BFS (fonte 1)', key:'BFS' },
    { m: medicoes.find(m=>m.tarefa.startsWith('DFS fonte 1')),    label:'DFS (fonte 1)', key:'DFS' },
    { m: medicoes.find(m=>m.tarefa.startsWith('Dijkstra')),       label:'Dijkstra',      key:'Dijkstra' },
    { m: medicoes.find(m=>m.tarefa.startsWith('Bellman')),        label:'Bellman-Ford',  key:'Bellman-Ford' },
    { m: medicoes.find(m=>m.tarefa.startsWith('Componentes')),    label:'Componentes',   key:'Componentes' },
  ].filter(r=>r.m)

  const W=920, H=400, PL=140, PR=110, PT=22, PB=38
  const iW=W-PL-PR, iH=H-PT-PB
  const rowH=iH/rows.length, bH=Math.min(rowH*0.3,14)
  const logMin=0, logMax=Math.log10(1100)
  const xS = v => PL+((Math.log10(Math.max(v,0.5))-logMin)/(logMax-logMin))*iW
  const xTicks=[1,5,10,50,100,500,1000]

  return (
    <>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{overflow:'visible'}}>
        {xTicks.map(t=>(
          <g key={t}>
            <line x1={xS(t)} x2={xS(t)} y1={PT} y2={PT+iH} stroke="rgba(255,255,255,0.07)" strokeWidth={1}/>
            <text x={xS(t)} y={PT+iH+16} textAnchor="middle" fill="rgba(255,255,255,0.38)" fontSize={11}>{t}</text>
          </g>
        ))}
        <line x1={PL} x2={PL} y1={PT} y2={PT+iH} stroke="rgba(255,255,255,0.22)" strokeWidth={1}/>
        {rows.map((_,i)=>i>0&&(
          <line key={i} x1={PL} x2={W-PR} y1={PT+i*rowH} y2={PT+i*rowH} stroke="rgba(255,255,255,0.04)" strokeWidth={1}/>
        ))}

        {rows.map((r,i)=>{
          const active=activeAlgos.has(r.key), color=algoColor(r.m.tarefa)
          const cy=PT+i*rowH+rowH/2, isHov=hov===r.key
          const avgW=xS(r.m.tempo_medio_ms)-PL, minW=xS(r.m.tempo_min_ms)-PL
          const varPct=((r.m.tempo_medio_ms-r.m.tempo_min_ms)/r.m.tempo_medio_ms*100).toFixed(0)
          return (
            <g key={r.key} onMouseEnter={()=>setHov(r.key)} onMouseLeave={()=>setHov(null)} style={{cursor:'pointer'}}>
              <text x={PL-10} y={cy+4} textAnchor="end"
                fill={isHov?'#fff':active?'rgba(255,255,255,0.62)':'rgba(255,255,255,0.2)'}
                fontSize={11} fontWeight={isHov?'700':'400'} style={{transition:'fill 0.18s'}}>
                {r.label}
              </text>
              {/* barra média */}
              <rect x={PL} y={cy-bH-1.5} width={avgW} height={bH} rx={3}
                fill={active?color:'#555'} fillOpacity={active?(isHov?0.62:0.38):0.1}
                style={{transition:'fill-opacity 0.2s,fill 0.2s'}}/>
              {/* barra mínima */}
              <rect x={PL} y={cy+1.5} width={minW} height={bH} rx={3}
                fill={active?color:'#555'} fillOpacity={active?(isHov?1:0.8):0.1}
                style={{transition:'fill-opacity 0.2s,fill 0.2s'}}/>
              {active && (
                <>
                  <text x={PL+avgW+5} y={cy-1} fill={color} fontSize={10} fillOpacity={0.65}>
                    {r.m.tempo_medio_ms.toFixed(1)}
                  </text>
                  <text x={PL+minW+5} y={cy+bH+9} fill={color} fontSize={10}>
                    {r.m.tempo_min_ms.toFixed(1)}
                  </text>
                </>
              )}
              {isHov && active && (
                <>
                  <rect x={W-PR+6} y={cy-34} width={102} height={62} rx={7}
                    fill="rgba(5,5,18,0.97)" stroke={`${color}55`} strokeWidth={1.5}/>
                  <text x={W-PR+16} y={cy-17} fill={color} fontSize={11} fontWeight="bold">{r.label}</text>
                  <text x={W-PR+16} y={cy-1} fill="rgba(255,255,255,0.65)" fontSize={10}>Var: ±{varPct}%</text>
                  <text x={W-PR+16} y={cy+14} fill="rgba(255,255,255,0.4)" fontSize={10}>{r.m.n_runs??1}× exec</text>
                  <text x={W-PR+16} y={cy+26} fill="rgba(255,255,255,0.3)" fontSize={9}>{r.m.complexidade_teorica}</text>
                </>
              )}
            </g>
          )
        })}
        <text x={PL+iW/2} y={H-8} textAnchor="middle" fill="rgba(255,255,255,0.38)" fontSize={10}>
          ms (escala logarítmica — cada marcação = 10× mais)
        </text>
      </svg>
      <ExplainedLegend
        items={[
          { label: 'Barra superior (mais clara)', color: 'rgba(255,255,255,0.52)', square: true, desc: 'Tempo médio calculado sobre 5 execuções com time.perf_counter(). Inclui variações do SO (agendador, cache de CPU).' },
          { label: 'Barra inferior (mais brilhante)', color: 'rgba(255,255,255,0.85)', square: true, desc: 'Tempo mínimo — melhor execução individual. Representa o desempenho do algoritmo sem overhead externo.' },
        ]}
        note="A distância entre as duas barras revela instabilidade: Dijkstra variou apenas ±7% (muito estável), enquanto DFS variou ±32% (mais sensível ao estado do SO). Bellman-Ford tem 1 execução, por isso mínimo = médio. Passe o mouse na linha para ver a variação exata."
      />
    </>
  )
}

/* ═══════════════════════════════════════════════════════════════════════════
   GRÁFICO 4 — Heatmap Comparativo
   ═══════════════════════════════════════════════════════════════════════════ */
function HeatmapChart({ medicoes, activeAlgos }) {
  const [hov, setHov] = useState(null)

  const bfsRows=medicoes.filter(m=>m.tarefa.startsWith('BFS fonte'))
  const dfsRows=medicoes.filter(m=>m.tarefa.startsWith('DFS fonte'))
  const bfsMem =bfsRows.reduce((s,m)=>s+m.memoria_pico_kb,0)/(bfsRows.length||1)
  const dfsMem =dfsRows.reduce((s,m)=>s+m.memoria_pico_kb,0)/(dfsRows.length||1)
  const bfsTime=bfsRows.reduce((s,m)=>s+m.tempo_medio_ms,0)/(bfsRows.length||1)
  const dfsTime=dfsRows.reduce((s,m)=>s+m.tempo_medio_ms,0)/(dfsRows.length||1)
  const bfsVar =bfsRows.reduce((s,m)=>s+(m.tempo_medio_ms-m.tempo_min_ms)/m.tempo_medio_ms,0)/(bfsRows.length||1)
  const dfsVar =dfsRows.reduce((s,m)=>s+(m.tempo_medio_ms-m.tempo_min_ms)/m.tempo_medio_ms,0)/(dfsRows.length||1)
  const dij=medicoes.find(m=>m.tarefa.startsWith('Dijkstra'))
  const bf =medicoes.find(m=>m.tarefa.startsWith('Bellman'))
  const cmp=medicoes.find(m=>m.tarefa.startsWith('Componentes'))
  const dijVar=(dij?(dij.tempo_medio_ms-dij.tempo_min_ms)/dij.tempo_medio_ms:0)
  const cmpVar=(cmp?(cmp.tempo_medio_ms-cmp.tempo_min_ms)/cmp.tempo_medio_ms:0)

  const rows=[
    {key:'BFS',         label:'BFS',         color:COLORS['BFS'],         time:bfsTime, mem:bfsMem, varN:bfsVar, cmplx:'O(V + E)',         nos:511 },
    {key:'DFS',         label:'DFS',         color:COLORS['DFS'],         time:dfsTime, mem:dfsMem, varN:dfsVar, cmplx:'O(V + E)',         nos:511 },
    {key:'Dijkstra',    label:'Dijkstra',    color:COLORS['Dijkstra'],    time:dij?.tempo_medio_ms, mem:dij?.memoria_pico_kb, varN:dijVar, cmplx:'O((V+E)·logV)', nos:4000},
    {key:'Bellman-Ford',label:'Bellman-Ford',color:COLORS['Bellman-Ford'],time:bf?.tempo_medio_ms,  mem:bf?.memoria_pico_kb,  varN:null,   cmplx:'O(V × E)',     nos:4000},
    {key:'Componentes', label:'Componentes', color:COLORS['Componentes Conexos (DFS global)'],time:cmp?.tempo_medio_ms,mem:cmp?.memoria_pico_kb,varN:cmpVar,cmplx:'O(V + E)',nos:4000},
  ]
  const maxTime=Math.max(...rows.map(r=>r.time??0))
  const maxMem =Math.max(...rows.map(r=>r.mem??0))
  const maxVar =Math.max(...rows.filter(r=>r.varN!=null).map(r=>r.varN))
  const maxNos =Math.max(...rows.map(r=>r.nos))

  const cols=[
    {label:'Tempo ↓',       sub:'menor = melhor',          get:r=>r.time,  fmt:v=>`${v.toFixed(1)} ms`,  norm:v=>v/maxTime },
    {label:'Memória ↓',     sub:'menor = melhor',          get:r=>r.mem,   fmt:v=>v>=1000?`${(v/1000).toFixed(1)}k KB`:`${v.toFixed(0)} KB`, norm:v=>v/maxMem },
    {label:'Variação ↓',    sub:'menor = mais estável',    get:r=>r.varN,  fmt:v=>v==null?'1× exec':`${(v*100).toFixed(0)}%`, norm:v=>v==null?0:v/maxVar },
    {label:'Nós visitados', sub:'alcance do algoritmo',    get:r=>r.nos,   fmt:v=>v.toLocaleString('pt-BR'), norm:v=>v/maxNos },
    {label:'Complexidade',  sub:'custo teórico assintótico', get:r=>r.cmplx, fmt:v=>v, norm:null },
  ]
  const W=920, H=360, PL=140, PT=60, rowH=48
  const colW=(W-PL-20)/cols.length
  const cmplxColor={'O(V + E)':'#4fc3f7','O((V+E)·logV)':'#ffd700','O(V × E)':'#ff2d78'}

  return (
    <>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{overflow:'visible'}}>
        {cols.map((c,ci)=>(
          <g key={c.label}>
            <text x={PL+ci*colW+colW/2} y={PT-24} textAnchor="middle" fill="rgba(255,255,255,0.78)" fontSize={12} fontWeight="700">{c.label}</text>
            <text x={PL+ci*colW+colW/2} y={PT-8} textAnchor="middle" fill="rgba(255,255,255,0.3)" fontSize={10}>{c.sub}</text>
          </g>
        ))}
        {rows.map((r,ri)=>{
          const active=activeAlgos.has(r.key), isHov=hov===r.key
          const y=PT+ri*rowH
          return (
            <g key={r.key} onMouseEnter={()=>setHov(r.key)} onMouseLeave={()=>setHov(null)} style={{cursor:'pointer'}}>
              {isHov&&<rect x={PL-4} y={y+2} width={W-PL-16} height={rowH-4} rx={6} fill="rgba(255,255,255,0.04)"/>}
              <text x={PL-12} y={y+rowH/2+4} textAnchor="end"
                fill={active?r.color:'rgba(255,255,255,0.18)'} fontSize={12} fontWeight="700"
                style={{transition:'fill 0.2s'}}>{r.label}</text>
              {cols.map((c,ci)=>{
                const val=c.get(r), norm=c.norm?c.norm(val??0):null
                const bg=c.norm==null?(cmplxColor[val]??'#333'):heatColor(norm)
                return (
                  <g key={c.label}>
                    <rect x={PL+ci*colW+3} y={y+4} width={colW-6} height={rowH-8} rx={5}
                      fill={bg} fillOpacity={active?(isHov?0.92:0.74):0.1}
                      style={{transition:'fill-opacity 0.2s'}}/>
                    <text x={PL+ci*colW+colW/2} y={y+rowH/2+5} textAnchor="middle"
                      fill={active?'#fff':'rgba(255,255,255,0.18)'}
                      fontSize={c.norm==null?10:11} fontWeight={c.norm==null?'400':'700'}
                      fontFamily={c.norm==null?'monospace':'inherit'}
                      style={{transition:'fill 0.2s'}}>
                      {val==null?'—':c.fmt(val)}
                    </text>
                  </g>
                )
              })}
            </g>
          )
        })}
        <defs>
          <linearGradient id="heatGrad" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0%"   stopColor="hsl(118,82%,40%)"/>
            <stop offset="50%"  stopColor="hsl(60,82%,40%)"/>
            <stop offset="100%" stopColor="hsl(0,82%,40%)"/>
          </linearGradient>
        </defs>
        <text x={PL} y={H-18} fill="rgba(255,255,255,0.3)" fontSize={10}>Escala de cor:</text>
        <rect x={PL+82} y={H-28} width={140} height={13} rx={3} fill="url(#heatGrad)" fillOpacity={0.82}/>
        <text x={PL+82}     y={H-6} fill="rgba(255,255,255,0.3)" fontSize={9}>Bom (menor)</text>
        <text x={PL+82+140} y={H-6} fill="rgba(255,255,255,0.3)" fontSize={9} textAnchor="end">Ruim (maior)</text>
      </svg>
      <ExplainedLegend
        items={[
          { label: 'Complexidade O(V + E)', color: '#4fc3f7', square: true, desc: 'Linear — cresce proporcionalmente ao número de vértices + arestas. Ideal para grafos densos.' },
          { label: 'Complexidade O((V+E)·logV)', color: '#ffd700', square: true, desc: 'Linearítmica — overhead da heap binária do Dijkstra. Ainda eficiente na prática.' },
          { label: 'Complexidade O(V × E)', color: '#ff2d78', square: true, desc: 'Quadrática — Bellman-Ford faz V−1 passagens sobre todas as E arestas. Muito mais lento em grafos grandes.' },
        ]}
        note="Cada célula é normalizada pela pior linha daquela coluna: 100% = pior valor, 0% = melhor valor. Variação = (médio − mínimo) / médio — mede instabilidade entre execuções. Nós visitados indica o alcance real do algoritmo no grafo."
      />
    </>
  )
}

/* ═══════════════════════════════════════════════════════════════════════════
   GRÁFICO 5 — Donut de Proporção de Memória
   ═══════════════════════════════════════════════════════════════════════════ */
function DonutChart({ medicoes, activeAlgos }) {
  const [hov, setHov] = useState(null)
  const bfsItems=medicoes.filter(m=>m.tarefa.startsWith('BFS fonte'))
  const dfsItems=medicoes.filter(m=>m.tarefa.startsWith('DFS fonte'))
  const bfsMem =bfsItems.reduce((s,m)=>s+m.memoria_pico_kb,0)/(bfsItems.length||1)
  const dfsMem =dfsItems.reduce((s,m)=>s+m.memoria_pico_kb,0)/(dfsItems.length||1)
  const dij=medicoes.find(m=>m.tarefa.startsWith('Dijkstra'))
  const bf =medicoes.find(m=>m.tarefa.startsWith('Bellman'))
  const cmp=medicoes.find(m=>m.tarefa.startsWith('Componentes'))

  const slices=[
    {key:'BFS',         label:'BFS',         mem:bfsMem,                    color:COLORS['BFS']},
    {key:'DFS',         label:'DFS',         mem:dfsMem,                    color:COLORS['DFS']},
    {key:'Dijkstra',    label:'Dijkstra',     mem:dij?.memoria_pico_kb??0,   color:COLORS['Dijkstra']},
    {key:'Bellman-Ford',label:'Bellman-Ford', mem:bf?.memoria_pico_kb??0,    color:COLORS['Bellman-Ford']},
    {key:'Componentes', label:'Componentes',  mem:cmp?.memoria_pico_kb??0,   color:COLORS['Componentes Conexos (DFS global)']},
  ]
  const total=slices.reduce((s,sl)=>s+sl.mem,0)
  const CX=220, CY=195, R=155, IR=88

  let angle=-Math.PI/2
  const built=slices.map(sl=>{
    const sweep=(sl.mem/total)*2*Math.PI
    const start=angle, end=angle+sweep, mid=(start+end)/2
    angle=end
    return {...sl, start, end, mid, pct:(sl.mem/total*100)}
  })

  function arcPath(start,end){
    const ox1=CX+R*Math.cos(start),oy1=CY+R*Math.sin(start)
    const ox2=CX+R*Math.cos(end),  oy2=CY+R*Math.sin(end)
    const ix1=CX+IR*Math.cos(end), iy1=CY+IR*Math.sin(end)
    const ix2=CX+IR*Math.cos(start),iy2=CY+IR*Math.sin(start)
    const large=end-start>Math.PI?1:0
    return `M ${ox1} ${oy1} A ${R} ${R} 0 ${large} 1 ${ox2} ${oy2} L ${ix1} ${iy1} A ${IR} ${IR} 0 ${large} 0 ${ix2} ${iy2} Z`
  }
  const hovSlice=built.find(s=>s.label===hov)??null

  return (
    <>
      <svg viewBox="0 0 920 420" width="100%" style={{overflow:'visible'}}>
        {built.map(sl=>{
          const active=activeAlgos.has(sl.key), isHov=hov===sl.label
          return (
            <g key={sl.label} onMouseEnter={()=>setHov(sl.label)} onMouseLeave={()=>setHov(null)}
              style={{cursor:'pointer', transformOrigin:`${CX}px ${CY}px`,
                transform:isHov?'scale(1.07)':'scale(1)', transition:'transform 0.18s'}}>
              <path d={arcPath(sl.start,sl.end)}
                fill={active?sl.color:'#555'} fillOpacity={active?(isHov?1:0.68):0.14}
                stroke="rgba(6,6,20,1)" strokeWidth={3}
                style={{transition:'fill-opacity 0.2s,fill 0.2s'}}/>
              {sl.pct>6&&active&&(
                <text x={CX+(R*0.72)*Math.cos(sl.mid)} y={CY+(R*0.72)*Math.sin(sl.mid)+4}
                  textAnchor="middle" fill="#fff" fontSize={12} fontWeight="700" fillOpacity={0.92} pointerEvents="none">
                  {sl.pct.toFixed(0)}%
                </text>
              )}
            </g>
          )
        })}
        {hovSlice?(
          <>
            <text x={CX} y={CY-16} textAnchor="middle" fill="#fff" fontSize={18} fontWeight="700">{hovSlice.pct.toFixed(1)}%</text>
            <text x={CX} y={CY+6}  textAnchor="middle" fill={hovSlice.color} fontSize={13} fontWeight="600">{hovSlice.label}</text>
            <text x={CX} y={CY+26} textAnchor="middle" fill="rgba(255,255,255,0.5)" fontSize={11}>{hovSlice.mem.toFixed(0)} KB</text>
          </>
        ):(
          <>
            <text x={CX} y={CY-8}  textAnchor="middle" fill="rgba(255,255,255,0.45)" fontSize={13}>Memória</text>
            <text x={CX} y={CY+12} textAnchor="middle" fill="rgba(255,255,255,0.45)" fontSize={13}>pico (KB)</text>
          </>
        )}

        {/* legenda lateral */}
        {built.map((sl,i)=>{
          const active=activeAlgos.has(sl.key), isHov=hov===sl.label
          return (
            <g key={sl.label} onMouseEnter={()=>setHov(sl.label)} onMouseLeave={()=>setHov(null)} style={{cursor:'pointer'}}>
              <rect x={430} y={50+i*62} width={14} height={14} rx={3}
                fill={sl.color} fillOpacity={active?(hov===null||isHov?1:0.38):0.2}/>
              <text x={450} y={50+i*62+12}
                fill={isHov?'#fff':active?'rgba(255,255,255,0.72)':'rgba(255,255,255,0.2)'}
                fontSize={13} fontWeight={isHov?'700':'500'} style={{transition:'fill 0.18s'}}>
                {sl.label}
              </text>
              <text x={450} y={50+i*62+28}
                fill={isHov?sl.color:active?'rgba(255,255,255,0.38)':'rgba(255,255,255,0.12)'}
                fontSize={11}>
                {sl.mem.toFixed(0)} KB — {sl.pct.toFixed(1)}% do total
              </text>
            </g>
          )
        })}
        <text x={430} y={390} fill="rgba(255,255,255,0.25)" fontSize={10}>
          Total (sem carregamento): {(total/1000).toFixed(1)}k KB
        </text>
      </svg>
      <ExplainedLegend
        items={[
          { label: 'Bellman-Ford (60%)', color: COLORS['Bellman-Ford'], desc: 'Domina o consumo de memória pois mantém V−1 iterações sobre todas as E arestas simultaneamente. Neste grafo: 3999 × 19717 ≈ 79M operações.' },
          { label: 'DFS (20%)', color: COLORS['DFS'], desc: 'Usa pilha de recursão proporcional à profundidade máxima do grafo. Consome ~2× mais memória que BFS pois mantém contexto de chamadas ativas.' },
          { label: 'BFS / Dijkstra / Componentes', color: 'rgba(255,255,255,0.5)', desc: 'Algoritmos com menor footprint de memória. BFS usa fila simples; Dijkstra usa heap mínima; Componentes usa marcação booleana.' },
        ]}
        note="Memória pico medida com tracemalloc (stdlib Python) — representa a maior alocação simultânea durante a execução, não o total acumulado. Passe o mouse nas fatias para ver os valores exatos."
      />
    </>
  )
}

/* ═══════════════════════════════════════════════════════════════════════════
   COMPONENTE PRINCIPAL — Benchmark
   ═══════════════════════════════════════════════════════════════════════════ */
export default function Benchmark() {
  const medicoes = reportData.medicoes
  const resumo   = reportData.resumo_comparativo
  const grafo    = reportData.grafo
  const casos    = reportData.casos_especiais_bellman_ford

  const [hoveredAlgo, setHoveredAlgo] = useState(null)
  const [sortCol,     setSortCol]     = useState('tempo_medio_ms')
  const [sortDir,     setSortDir]     = useState(-1)
  const [barsReady,   setBarsReady]   = useState(false)
  const [activeAlgos, setActiveAlgos] = useState(() => new Set(ALGO_GROUPS.map(g=>g.key)))
  const allActive = activeAlgos.size === ALGO_GROUPS.length

  function toggleAlgo(key) {
    setActiveAlgos(prev => {
      const next = new Set(prev)
      if (next.has(key)) { if (next.size > 1) next.delete(key) } else next.add(key)
      return next
    })
  }

  useEffect(() => { const t=setTimeout(()=>setBarsReady(true),80); return ()=>clearTimeout(t) }, [])

  const maxTempo = useMemo(()=>Math.max(...medicoes.map(m=>m.tempo_medio_ms)),[medicoes])

  const sortedMedicoes = useMemo(()=>[...medicoes].sort((a,b)=>{
    const av=a[sortCol]??0, bv=b[sortCol]??0; return sortDir*(bv-av)
  }),[medicoes,sortCol,sortDir])

  function handleSort(col){ if(col===sortCol)setSortDir(d=>-d); else{setSortCol(col);setSortDir(-1)} }
  function sortIcon(col){ if(col!==sortCol)return ' ↕'; return sortDir===-1?' ↓':' ↑' }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Painel de Benchmark</h1>
      <p className={styles.subtitle}>
        Comparação de desempenho dos algoritmos no dataset Spotify
        ({grafo.vertices.toLocaleString('pt-BR')} vértices · {grafo.arestas.toLocaleString('pt-BR')} arestas · {grafo.tipo})
      </p>

      {/* ── Gráfico de barras ── */}
      <section className={styles.card}>
        <h2 className={styles.cardTitle}>Tempo médio de execução (ms)</h2>
        <div className={styles.chart}>
          {medicoes.map(m => {
            const label=shortLabel(m.tarefa), pct=barsReady?(m.tempo_medio_ms/maxTempo)*100:0
            const color=algoColor(m.tarefa), isHov=hoveredAlgo===m.tarefa
            return (
              <div key={m.tarefa} className={`${styles.barRow} ${isHov?styles.barRowHovered:''}`}
                onMouseEnter={()=>setHoveredAlgo(m.tarefa)} onMouseLeave={()=>setHoveredAlgo(null)}>
                <div className={styles.barLabel} style={{color:isHov?'#fff':undefined}}>{label}</div>
                <div className={styles.barTrack}>
                  <div className={styles.barFill} style={{width:`${pct}%`,background:color,boxShadow:isHov?`0 0 16px ${color}88`:'none'}}/>
                  <span className={styles.barValue}>{m.tempo_medio_ms.toFixed(2)} ms</span>
                </div>
                {isHov&&(
                  <div className={styles.tooltip}>
                    <div style={{color,fontWeight:700,marginBottom:6}}>● {label}</div>
                    <div>Tempo médio: <strong>{m.tempo_medio_ms.toFixed(2)} ms</strong></div>
                    <div>Tempo mínimo: <strong>{m.tempo_min_ms.toFixed(2)} ms</strong></div>
                    <div>Memória pico: <strong>{m.memoria_pico_kb.toFixed(0)} KB</strong></div>
                    <div>Complexidade: <span style={{fontFamily:'monospace',color:'#ffd700'}}>{m.complexidade_teorica}</span></div>
                    <div>Execuções: <strong>{m.n_runs??1}</strong></div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </section>

      {/* ── Tabela ── */}
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
                <th className={styles.sortable} onClick={()=>handleSort('tempo_medio_ms')}>Tempo médio (ms){sortIcon('tempo_medio_ms')}</th>
                <th className={styles.sortable} onClick={()=>handleSort('tempo_min_ms')}>Tempo mín. (ms){sortIcon('tempo_min_ms')}</th>
                <th className={styles.sortable} onClick={()=>handleSort('memoria_pico_kb')}>Memória pico (KB){sortIcon('memoria_pico_kb')}</th>
                <th>Complexidade</th>
                <th className={styles.sortable} onClick={()=>handleSort('n_runs')}>Execuções{sortIcon('n_runs')}</th>
              </tr>
            </thead>
            <tbody>
              {sortedMedicoes.map(m=>(
                <tr key={m.tarefa} className={hoveredAlgo===m.tarefa?styles.rowHovered:''}
                  onMouseEnter={()=>setHoveredAlgo(m.tarefa)} onMouseLeave={()=>setHoveredAlgo(null)}>
                  <td><span className={styles.dot} style={{background:algoColor(m.tarefa)}}/>{m.tarefa}</td>
                  <td className={styles.num}>{m.tempo_medio_ms.toFixed(3)}</td>
                  <td className={styles.num}>{m.tempo_min_ms.toFixed(3)}</td>
                  <td className={styles.num}>{m.memoria_pico_kb.toFixed(1)}</td>
                  <td className={styles.mono}>{m.complexidade_teorica}</td>
                  <td className={styles.num}>{m.n_runs??1}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* ── Resumo ── */}
      <section className={styles.cardRow}>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>Mais rápido</div>
          <div className={styles.statVal} style={{color:'#00e676'}}>{resumo.mais_rapido.algoritmo}</div>
          <div className={styles.statSub}>{resumo.mais_rapido.tempo_medio_ms.toFixed(2)} ms</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>Mais lento</div>
          <div className={styles.statVal} style={{color:'#ff2d78'}}>{resumo.mais_lento.algoritmo}</div>
          <div className={styles.statSub}>{resumo.mais_lento.tempo_medio_ms.toFixed(2)} ms</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>BF mais lento que Dijkstra</div>
          <div className={styles.statVal} style={{color:'#ffd700'}}>{resumo.razao_bf_vs_dijkstra}×</div>
          <div className={styles.statSub}>vezes mais lento</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statLabel}>BF mais lento que BFS</div>
          <div className={styles.statVal} style={{color:'#ffd700'}}>{resumo.razao_bf_vs_bfs}×</div>
          <div className={styles.statSub}>vezes mais lento</div>
        </div>
      </section>

      {/* ── Casos Bellman-Ford ── */}
      <section className={styles.card}>
        <h2 className={styles.cardTitle}>Casos especiais — Bellman-Ford</h2>
        <div className={styles.bfGrid}>
          <div className={styles.bfCase}>
            <div className={styles.bfCaseTitle}>✅ Peso negativo sem ciclo</div>
            <div className={styles.bfDesc}>{casos.peso_negativo_sem_ciclo.descricao}</div>
            <div className={styles.bfPath}>Origem: <strong>{casos.peso_negativo_sem_ciclo.origem}</strong> → Destino: <strong>{casos.peso_negativo_sem_ciclo.destino}</strong></div>
            <div className={styles.bfPath}>Caminho: {casos.peso_negativo_sem_ciclo.caminho.join(' → ')}</div>
            <div className={styles.bfPath}>Custo: <strong style={{color:'#00e676'}}>{casos.peso_negativo_sem_ciclo.custo}</strong> · {casos.peso_negativo_sem_ciclo.tempo_ms} ms</div>
            <div className={styles.bfObs}>{casos.peso_negativo_sem_ciclo.observacao}</div>
          </div>
          <div className={styles.bfCase}>
            <div className={styles.bfCaseTitle}>⛔ Ciclo negativo detectado</div>
            <div className={styles.bfDesc}>{casos.ciclo_negativo_detectado.descricao}</div>
            <div className={styles.bfPath}>Custo do ciclo: <strong style={{color:'#ff2d78'}}>{casos.ciclo_negativo_detectado.custo_do_ciclo}</strong></div>
            <div className={styles.bfPath}>Detecção: <strong style={{color:'#ff2d78'}}>{casos.ciclo_negativo_detectado.ciclo_negativo_detectado?'SIM':'NÃO'}</strong></div>
            <div className={styles.bfObs}>{casos.ciclo_negativo_detectado.observacao}</div>
          </div>
        </div>
      </section>

      {/* ── Discussão ── */}
      <section className={styles.card}>
        <h2 className={styles.cardTitle}>Discussão crítica</h2>
        <div className={styles.discuss}>
          {Object.entries(reportData.discussao_critica).map(([algo,texto])=>(
            <div key={algo} className={styles.discussItem}>
              <div className={styles.discussAlgo} style={{color:algoColor(algo)}}>{algo}</div>
              <div className={styles.discussText}>{texto}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ════════════ ANÁLISE VISUAL AVANÇADA ════════════ */}
      <div className={styles.chartsSectionHeader}>
        <h2 className={styles.chartsSectionTitle}>Análise Visual Avançada</h2>
        <p className={styles.chartsSectionSub}>
          5 gráficos interativos — passe o mouse para explorar. Use os filtros para isolar algoritmos.
        </p>
      </div>

      {/* filtros */}
      <div className={styles.filtersRow}>
        <span className={styles.filtersLabel}>Filtrar:</span>
        <div className={styles.filters}>
          {ALGO_GROUPS.map(g=>(
            <button key={g.key} onClick={()=>toggleAlgo(g.key)} className={styles.filterPill}
              style={{borderColor:g.color, color:activeAlgos.has(g.key)?g.color:'rgba(255,255,255,0.28)',
                background:activeAlgos.has(g.key)?`${g.color}18`:'transparent'}}>
              <span style={{display:'inline-block',width:8,height:8,borderRadius:'50%',
                background:activeAlgos.has(g.key)?g.color:'rgba(255,255,255,0.22)',marginRight:6,verticalAlign:'middle'}}/>
              {g.label}
            </button>
          ))}
          {!allActive&&(
            <button onClick={()=>setActiveAlgos(new Set(ALGO_GROUPS.map(g=>g.key)))} className={styles.filterReset}>
              Limpar ×
            </button>
          )}
        </div>
      </div>

      {/* ── Gráfico 1 ── */}
      <section className={styles.chartCard}>
        <div className={styles.chartCardHeader}>
          <h3 className={styles.chartCardTitle}>1 — Dispersão: Memória × Tempo</h3>
          <p className={styles.chartCardDesc}>
            Cada ponto é uma medição de algoritmo. Posição horizontal = velocidade (escala log); posição vertical = consumo de memória.
            Ideal: canto inferior esquerdo. Eixo X logarítmico acomoda a diferença de 117× entre BFS (~7 ms) e Bellman-Ford (~852 ms).
          </p>
        </div>
        <ScatterChart medicoes={medicoes} activeAlgos={activeAlgos}/>
      </section>

      {/* ── Gráfico 2 ── */}
      <section className={styles.chartCard}>
        <div className={styles.chartCardHeader}>
          <h3 className={styles.chartCardTitle}>2 — BFS vs DFS por Fonte Musical</h3>
          <p className={styles.chartCardDesc}>
            Três músicas-origem distintas foram usadas para verificar se o desempenho dos algoritmos é consistente
            independente do ponto de partida. Cada par de barras = uma fonte. Linha tracejada = tempo mínimo atingido.
          </p>
        </div>
        <GroupedBarChart medicoes={medicoes} activeAlgos={activeAlgos}/>
      </section>

      {/* ── Gráfico 3 ── */}
      <section className={styles.chartCard}>
        <div className={styles.chartCardHeader}>
          <h3 className={styles.chartCardTitle}>3 — Estabilidade: Tempo Mínimo vs Médio</h3>
          <p className={styles.chartCardDesc}>
            Para cada algoritmo há duas barras na mesma linha: a superior (mais clara) é o tempo médio e
            a inferior (mais brilhante) é o mínimo. Escala logarítmica permite comparar do BFS (7 ms) ao Bellman-Ford (852 ms)
            em um único gráfico. A diferença entre barras revela instabilidade de execução.
          </p>
        </div>
        <MinAvgChart medicoes={medicoes} activeAlgos={activeAlgos}/>
      </section>

      {/* ── Gráfico 4 ── */}
      <section className={styles.chartCard}>
        <div className={styles.chartCardHeader}>
          <h3 className={styles.chartCardTitle}>4 — Heatmap Comparativo: Múltiplas Métricas</h3>
          <p className={styles.chartCardDesc}>
            Grade algoritmo × métrica com coloração de <span style={{color:'hsl(118,82%,52%)'}}>verde</span> (melhor relativo) a <span style={{color:'hsl(0,82%,58%)'}}>vermelho</span> (pior relativo).
            Cada coluna é normalizada independentemente. A coluna "Complexidade" usa cores fixas por categoria teórica.
            Passe o mouse em uma linha para destacá-la.
          </p>
        </div>
        <HeatmapChart medicoes={medicoes} activeAlgos={activeAlgos}/>
      </section>

      {/* ── Gráfico 5 ── */}
      <section className={styles.chartCard}>
        <div className={styles.chartCardHeader}>
          <h3 className={styles.chartCardTitle}>5 — Proporção de Memória Pico por Algoritmo</h3>
          <p className={styles.chartCardDesc}>
            Fatia da memória pico total consumida por cada algoritmo (excluindo o carregamento do grafo).
            Bellman-Ford domina com ~60% — reflexo direto de sua complexidade O(V×E) que exige manter
            estruturas de tamanho proporcional ao produto vértices × arestas.
          </p>
        </div>
        <DonutChart medicoes={medicoes} activeAlgos={activeAlgos}/>
      </section>
    </div>
  )
}
