import styles from './Sobre.module.css'

const ALGORITHMS = [
  {
    name: 'BFS',
    full: 'Busca em Largura',
    color: '#00e676',
    complexity: 'O(V + E)',
    tempo: '18,43 ms',
    desc: 'Explora os nós por camadas de distância a partir da origem. Garante o menor número de saltos. No dataset Spotify, cada camada reúne músicas com grau de separação equivalente.',
  },
  {
    name: 'DFS',
    full: 'Busca em Profundidade',
    color: '#d500f9',
    complexity: 'O(V + E)',
    tempo: '428,01 ms',
    desc: 'Mergulha o mais fundo possível antes de retroceder. Detecta ciclos e classifica as arestas em: árvore, retorno, avanço e cruzada. Ciclo detectado na rede Spotify.',
  },
  {
    name: 'Dijkstra',
    full: 'Caminho Mínimo',
    color: '#ffd700',
    complexity: 'O((V+E) log V)',
    tempo: '49,90 ms',
    desc: 'Encontra o caminho de menor custo entre duas músicas. Pesos = distância euclidiana entre vetores de atributos sonoros (danceability, energy, valence…). 38× mais rápido que Bellman-Ford.',
  },
  {
    name: 'Bellman-Ford',
    full: 'Caminho com Pesos Negativos',
    color: '#ff2d78',
    complexity: 'O(V × E)',
    tempo: '1.895,43 ms',
    desc: 'Generalização do Dijkstra que suporta pesos negativos e detecta ciclos negativos. Demonstrado com grafos sintéticos — indispensável quando o grafo pode ter arestas negativas.',
  },
]

const DATASET_ROWS = [
  { label: 'Fonte',             value: 'Spotify Tracks Dataset (Kaggle)' },
  { label: 'Nós',               value: '4.000 músicas' },
  { label: 'Arestas',           value: '19.717 conexões' },
  { label: 'Tipo',              value: 'Não-dirigido, ponderado' },
  { label: 'Critério de aresta', value: 'k-NN por distância euclidiana' },
  { label: 'Atributos usados',  value: 'danceability, energy, loudness, speechiness, acousticness, instrumentalness, liveness, valence, tempo' },
  { label: 'Grau mínimo',       value: '7' },
  { label: 'Grau máximo',       value: '22' },
  { label: 'Grau médio',        value: '9,86' },
  { label: 'Componentes conexas', value: '8' },
]

const HOW_TO = [
  { icon: '⚡', page: 'Explorar Rede',   desc: 'Grafo de força interativo. Clique em um nó para ver detalhes da música. Ative "Caminho Dijkstra" para traçar o menor caminho entre duas músicas — nós de componentes diferentes ficam escuros.' },
  { icon: '⬡', page: 'Benchmark',       desc: 'Comparação de desempenho dos 4 algoritmos. Passe o mouse nas barras para ver memória, tempo mínimo e complexidade. Clique nos cabeçalhos da tabela para ordenar.' },
  { icon: '▦', page: 'BFS / DFS',       desc: 'Animação passo a passo das camadas BFS. Troque entre as 3 origens e ajuste a velocidade. Na aba DFS veja a classificação de arestas e a ordem de visita com busca por música.' },
  { icon: '⇢', page: 'Dijkstra vs BF',  desc: 'Comparação lado a lado dos dois algoritmos de caminho mínimo nos mesmos pares de músicas. Como os pesos são ≥ 0, ambos chegam ao mesmo resultado — mas Dijkstra é muito mais eficiente.' },
]

export default function Sobre() {
  return (
    <div className={styles.page}>
      <div className={styles.hero}>
        <span className={styles.badge}>CESAR School · Teoria dos Grafos 2026 · Parte 2</span>
        <h1 className={styles.title}>Sobre o Projeto</h1>
        <p className={styles.subtitle}>
          Rede de similaridade musical construída a partir do Spotify Tracks Dataset.
          BFS, DFS, Dijkstra e Bellman-Ford foram implementados do zero em Python 3.11
          e aplicados a um grafo de 4.000 músicas e 19.717 conexões.
        </p>
      </div>

      {/* Dataset */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Dataset — Rede Musical Spotify</h2>
        <div className={styles.dsCard}>
          {DATASET_ROWS.map(d => (
            <div key={d.label} className={styles.dsRow}>
              <span className={styles.dsLabel}>{d.label}</span>
              <span className={styles.dsVal}>{d.value}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Algoritmos */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Algoritmos aplicados ao dataset</h2>
        <div className={styles.algoGrid}>
          {ALGORITHMS.map(a => (
            <div key={a.name} className={styles.algoCard} style={{ borderColor: a.color + '33' }}>
              <div className={styles.algoHeader}>
                <span className={styles.algoName} style={{ color: a.color }}>{a.name}</span>
                <span className={styles.algoBadge} style={{ color: a.color, borderColor: a.color + '44' }}>
                  {a.complexity}
                </span>
                <span className={styles.algoTempo}>{a.tempo}</span>
              </div>
              <div className={styles.algoFull}>{a.full}</div>
              <div className={styles.algoDesc}>{a.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Como usar */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Como usar cada aba</h2>
        <div className={styles.howGrid}>
          {HOW_TO.map(h => (
            <div key={h.page} className={styles.howCard}>
              <div className={styles.howIcon}>{h.icon}</div>
              <div className={styles.howPage}>{h.page}</div>
              <div className={styles.howDesc}>{h.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Nota técnica */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Nota técnica</h2>
        <div className={styles.ruleList}>
          {[
            'Algoritmos implementados do zero — sem NetworkX, igraph ou graph-tool',
            'heapq (stdlib Python) utilizado internamente pelo Dijkstra',
            'Pesos = distância euclidiana normalizada entre vetores de atributos (≥ 0)',
            'Bellman-Ford demonstrado com grafos sintéticos com pesos negativos e ciclos negativos',
            'Benchmark medido com tracemalloc (memória) e time.perf_counter (tempo), média de 5 execuções',
          ].map((r, i) => (
            <div key={i} className={styles.ruleItem}>
              <span className={styles.ruleCheck}>✓</span>
              <span>{r}</span>
            </div>
          ))}
        </div>
      </section>

      <div className={styles.footer}>
        CESAR School · Teoria dos Grafos 2026 · Python 3.11 + React 18 · Parte 2
      </div>
    </div>
  )
}
