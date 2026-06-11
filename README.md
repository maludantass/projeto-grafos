# Projeto Grafos — Rede de Aeroportos do Brasil + Comparação de Algoritmos

**CESAR School · Teoria dos Grafos 2026**

Implementação própria de BFS, DFS, Dijkstra e Bellman-Ford (sem NetworkX ou similares) aplicada a dois datasets:
- **Parte 1:** Rede de aeroportos brasileiros (20 nós, 23 arestas)
- **Parte 2:** Rede de músicas do Spotify por similaridade sonora (4.000 nós, 19.717 arestas)

---

## Sumário

1. [Estrutura do Projeto](#estrutura-do-projeto)
2. [Instalação](#instalação)
3. [Como Executar — Parte 1 (Aeroportos)](#como-executar--parte-1-aeroportos)
4. [Como Executar — Parte 2 (Spotify)](#como-executar--parte-2-spotify)
5. [Frontend Interativo](#frontend-interativo)
6. [Testes](#testes)
7. [Modelagem do Grafo — Parte 1](#modelagem-do-grafo--parte-1)
8. [Dataset — Parte 2](#dataset--parte-2)
9. [Saídas Geradas](#saídas-geradas)
10. [Resultados de Benchmark](#resultados-de-benchmark)

---

## Estrutura do Projeto

```
projeto-grafos/
├── README.md
├── requirements.txt
├── data/
│   ├── aeroportos_data.csv          # 20 aeroportos (IATA, cidade, região)
│   ├── adjacencias_aeroportos.csv   # arestas construídas pelo grupo
│   ├── rotas.csv                    # 7 pares origem-destino para Dijkstra
│   └── dataset_parte2/
│       ├── dataset_parte2.csv       # 4.000 músicas do Spotify
│       ├── musicas_nos.csv          # nós do grafo (id, nome, artista, gênero)
│       ├── adjacencias_musicas.csv  # arestas por similaridade euclidiana
│       └── descricao_dataset.txt    # descrição e critérios de construção
├── out/                             # saídas geradas pelos scripts
│   ├── global.json
│   ├── regioes.json
│   ├── ego_aeroportos.csv
│   ├── graus.csv
│   ├── rankings.json
│   ├── distancias_rotas.csv
│   ├── pesos_arestas.json
│   ├── arvore_percurso.html
│   ├── grafo_interativo.html
│   ├── parte2_report.json
│   ├── viz1_distribuicao_graus.png
│   ├── viz2_ranking_aeroportos.png
│   ├── viz3_comparacao_regioes.png
│   ├── viz4_bfs_camadas_BSB.png
│   ├── viz10_1_heatmap_adjacencias.png
│   ├── viz10_2_centralidade_grau.png
│   ├── viz10_3_vulnerabilidade_barras.png
│   ├── viz10_4_mapa_conectividade.png
│   ├── index.html                   # landing page com links para Parte 1 e 2
│   └── parte2/
│       └── index.html               # frontend React da Parte 2 (build)
├── src/
│   ├── cli.py                       # interface de linha de comando
│   ├── solve.py                     # execução completa (Parte 2) automatizada
│   ├── metricas.py                  # métricas globais, regionais e ego-redes (Parte 1)
│   ├── viz.py                       # visualizações matplotlib (Parte 1)
│   ├── arvore_percurso.py           # visualização do percurso da Parte 1 via pyvis
│   ├── avd_exploratorias.py         # visualizações exploratórias (Parte 1)
│   ├── avd_explanatorias.py         # visualizações explanatórias (Parte 1)
│   ├── construir_grafo_spotify.py   # script de construção do grafo do Spotify
│   ├── performance_parte2.py        # benchmark da Parte 2
│   └── graphs/
│       ├── graph.py                 # estrutura de dados: lista de adjacência
│       ├── algorithms.py            # BFS, DFS, Dijkstra, Bellman-Ford
│       └── io.py                    # leitura e validação dos CSVs
├── frontend/                        # código-fonte do frontend React (Parte 2)
│   ├── src/
│   └── package.json
└── tests/
    ├── test_bfs.py
    ├── test_dfs.py
    ├── test_dijkstra.py
    ├── test_bellman_ford.py
    └── test_bfs_dfs_dataset2.py     # testes para o dataset do Spotify
```

---

## Instalação

**Pré-requisitos:** Python 3.11+ e Node.js 18+

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd projeto-grafos

# 2. Instale as dependências Python
pip install -r requirements.txt
```

---

## Como Executar — Parte 1 (Aeroportos)

Todos os comandos usam `python -m src.cli` a partir da raiz do projeto.

### BFS

```bash
# BFS a partir de Recife
python -m src.cli --dataset ./data/aeroportos_data.csv --alg BFS --source REC --out ./out/

# BFS a partir de Manaus
python -m src.cli --dataset ./data/aeroportos_data.csv --alg BFS --source MAO --out ./out/

# BFS a partir de Brasília
python -m src.cli --dataset ./data/aeroportos_data.csv --alg BFS --source BSB --out ./out/
```

### DFS

```bash
# DFS a partir de Recife
python -m src.cli --dataset ./data/aeroportos_data.csv --alg DFS --source REC --out ./out/

# DFS a partir de São Paulo (Guarulhos)
python -m src.cli --dataset ./data/aeroportos_data.csv --alg DFS --source GRU --out ./out/
```

### Dijkstra

```bash
# Par obrigatório: Recife → Porto Alegre
python -m src.cli --dataset ./data/aeroportos_data.csv --alg DIJKSTRA --source REC --target POA --out ./out/

# Par obrigatório: Manaus → São Paulo
python -m src.cli --dataset ./data/aeroportos_data.csv --alg DIJKSTRA --source MAO --target GRU --out ./out/

# Outros pares
python -m src.cli --dataset ./data/aeroportos_data.csv --alg DIJKSTRA --source BEL --target CNF --out ./out/
python -m src.cli --dataset ./data/aeroportos_data.csv --alg DIJKSTRA --source FOR --target CWB --out ./out/
python -m src.cli --dataset ./data/aeroportos_data.csv --alg DIJKSTRA --source GIG --target MAO --out ./out/
```

### Bellman-Ford

```bash
# Caminho mínimo com pesos positivos
python -m src.cli --dataset ./data/aeroportos_data.csv --alg BELLMAN_FORD --source REC --target POA --out ./out/

# Caminho mínimo Manaus → São Paulo
python -m src.cli --dataset ./data/aeroportos_data.csv --alg BELLMAN_FORD --source MAO --target GRU --out ./out/
```

### Executar geração de saídas da Parte 1 (Métricas e Visualizações)

Para gerar todas as métricas, visualizações matplotlib e páginas HTML interativas da Parte 1, execute os seguintes scripts:

```bash
# 1. Gera métricas globais, regionais, ego-redes, graus e rankings (global.json, regioes.json, etc.)
python -m src.metricas

# 2. Gera visualizações (viz1_distribuicao_graus.png, viz2_ranking_aeroportos.png, viz3_comparacao_regioes.png, viz4_bfs_camadas_BSB.png)
python -m src.viz

# 3. Gera a visualização interativa do percurso Recife-POA e Manaus-GRU (arvore_percurso.html)
python -m src.arvore_percurso

# 4. Gera análises exploratórias (viz10_1_heatmap_adjacencias.png e viz10_2_centralidade_grau.png)
python -m src.avd_exploratorias

# 5. Gera análises explanatórias (viz10_3_vulnerabilidade_barras.png e viz10_4_mapa_conectividade.png)
python -m src.avd_explanatorias
```

---

## Como Executar — Parte 2 (Spotify)

```bash
# BFS a partir de uma música (ID Spotify)
python -m src.cli --dataset ./data/dataset_parte2/ --alg BFS --source 3pyQ7RB5P8iwZMkPAeZ3ym --out ./out/

# DFS a partir de uma música
python -m src.cli --dataset ./data/dataset_parte2/ --alg DFS --source 3pyQ7RB5P8iwZMkPAeZ3ym --out ./out/

# Dijkstra entre duas músicas
python -m src.cli --dataset ./data/dataset_parte2/ --alg DIJKSTRA \
  --source 3pyQ7RB5P8iwZMkPAeZ3ym --target 4cpdzzOLPuoRLnaJBcQFYp --out ./out/

# Bellman-Ford entre duas músicas
python -m src.cli --dataset ./data/dataset_parte2/ --alg BELLMAN_FORD \
  --source 3pyQ7RB5P8iwZMkPAeZ3ym --target 4cpdzzOLPuoRLnaJBcQFYp --out ./out/
```

### Executar tudo de uma vez (solve.py)

```bash
# Gera todas as saídas e arquivos JSON de BFS, DFS, Dijkstra e Bellman-Ford da Parte 2 automaticamente
python -m src.solve
```

### Benchmark completo da Parte 2

```bash
# Roda BFS, DFS, Dijkstra e Bellman-Ford com medição de tempo e memória
# Gera out/parte2_report.json
python -m src.performance_parte2
```

---

## Frontend Interativo

O frontend React visualiza a Parte 2 (rede Spotify) com grafo de força, BFS/DFS animado, benchmark e comparação de algoritmos.

### Abrir versão já construída (sem instalar nada)

```bash
# Abra diretamente no navegador:
out/index.html
```

A página inicial (`out/index.html`) tem links para:
- **Parte 1** → `out/grafo_interativo.html` (grafo de aeroportos interativo)
- **Parte 2** → `out/parte2/index.html` (app React completo)

### Rodar em modo de desenvolvimento

```bash
cd frontend
npm install
npm run dev
# Acesse: http://localhost:5173
```

### Build de produção

```bash
cd frontend
npm run build
# Gera out/parte2/index.html (arquivo único autocontido)
```

### Funcionalidades do Frontend (Parte 2)

| Aba | Descrição |
|-----|-----------|
| **Início** | Landing animada da Parte 2 |
| **Explorar Rede** | Grafo de força interativo com 4.000 nós; clique, busca e caminho mínimo com Dijkstra |
| **Benchmark** | Barras animadas, tabela ordenável, hover com detalhes; dados de `out/parte2_report.json` |
| **BFS / DFS** | Animação step-by-step das camadas BFS; busca de músicas na ordem de visita; nós clicáveis |
| **Dijkstra vs BF** | Comparação lado a lado dos dois algoritmos nos mesmos pares |

---

## Testes

```bash
# Rodar todos os testes
pytest tests/ -v

# Rodar um módulo específico
pytest tests/test_bfs.py -v
pytest tests/test_dfs.py -v
pytest tests/test_dijkstra.py -v
pytest tests/test_bellman_ford.py -v
pytest tests/test_bfs_dfs_dataset2.py -v
```

### Cobertura dos testes

| Arquivo | O que testa |
|---------|-------------|
| `test_bfs.py` | Níveis corretos em grafo pequeno, ordem de visita, robustez em grafo desconexo |
| `test_dfs.py` | Detecção de ciclo, classificação de arestas (árvore/retorno/avanço/cruzada), tempos entrada/saída |
| `test_dijkstra.py` | Caminhos e custos corretos com pesos ≥ 0; rejeição de pesos negativos |
| `test_bellman_ford.py` | Pesos negativos sem ciclo (distâncias corretas); detecção de ciclo negativo (flag) |
| `test_bfs_dfs_dataset2.py` | Invariantes do BFS/DFS (níveis, visita, ciclos) no grafo maior do Spotify (Parte 2) |

---

## Modelagem do Grafo — Parte 1

### Nós
20 aeroportos brasileiros identificados pelo código IATA:

| Região | Aeroportos |
|--------|-----------|
| Norte | MAO, BEL, PVH, RBR |
| Nordeste | REC, SSA, FOR, NAT, JPA, MCZ |
| Centro-Oeste | BSB, CGO |
| Sudeste | GRU, GIG, CNF, CGH, VCP |
| Sul | CWB, FLN, POA |

### Arestas (23 arestas não-direcionadas)
As arestas foram construídas com base em dois critérios:

- **`regional` (15 arestas):** conecta aeroportos da mesma região, representando fluxo intrarregional
- **`hub` (8 arestas):** conecta aeroportos de regiões distintas via hubs nacionais (BSB, GRU, SSA)

### Modelo de Pesos

| Tipo de Conexão | Peso | Justificativa |
|-----------------|------|---------------|
| Regional (mesma região) | 1.0 | Curta distância, sem mudança de região |
| Hub regional → hub nacional | 2.0 | Mudança de região, passa por hub intermediário |
| Conexão inter-regional via hub | 3.0 | Maior distância, penalidade por salto longo |

**Fórmula:** `peso = 1 + penalidade_região + penalidade_hub`

O grafo é **não-direcionado** e **conectado** — todos os 20 aeroportos são alcançáveis entre si.

### Métricas Globais

| Métrica | Valor |
|---------|-------|
| Ordem \|V\| | 20 aeroportos |
| Tamanho \|E\| | 23 arestas |
| Densidade | 0.1211 |
| Aeroporto mais conectado | **BSB** (grau 6) |
| Maior densidade local | **CGH** (densidade ego = 1.0) |

### Métricas por Região (subgrafos induzidos)

| Região | \|V\| | \|E\| | Densidade |
|--------|-------|-------|-----------|
| Centro-Oeste | 2 | 1 | 1.000 |
| Sul | 3 | 2 | 0.667 |
| Norte | 4 | 3 | 0.500 |
| Sudeste | 5 | 4 | 0.400 |
| Nordeste | 6 | 5 | 0.333 |

### Caminhos Mínimos (Dijkstra)

| Origem | Destino | Custo | Caminho |
|--------|---------|-------|---------|
| MAO | GRU | 5.0 | MAO → BSB → GRU |
| REC | POA | 9.0 | REC → SSA → GIG → GRU → CWB → FLN → POA |
| BEL | CNF | 5.0 | BEL → BSB → CNF |
| RBR | SSA | 9.0 | RBR → PVH → MAO → BEL → FOR → NAT → JPA → REC → SSA |
| FOR | CWB | 7.0 | FOR → BSB → GRU → CWB |
| GIG | MAO | 6.0 | GIG → CNF → BSB → MAO |
| PVH | FLN | 9.0 | PVH → MAO → BSB → GRU → CWB → FLN |

---

## Dataset — Parte 2

**Spotify Tracks Dataset** (Kaggle) — rede de similaridade musical

| Métrica | Valor |
|---------|-------|
| Vértices \|V\| | 4.000 músicas |
| Arestas \|E\| | 19.717 conexões |
| Tipo | Não-dirigido, ponderado |
| Grau mínimo | 7 |
| Grau máximo | 22 |
| Grau médio | 9,86 |
| Componentes conexas | 8 |

**Critério de aresta:** duas músicas são conectadas se a distância euclidiana entre seus vetores de atributos (danceability, energy, loudness, speechiness, acousticness, instrumentalness, liveness, valence, tempo) for menor que um limiar `k`. Cada música possui no mínimo 7 vizinhos (k-NN aproximado).

**Pesos:** distância euclidiana normalizada entre os vetores de atributos (pesos ≥ 0, adequados para Dijkstra). Para Bellman-Ford, foram construídos casos sintéticos com pesos negativos para demonstrar a vantagem do algoritmo.

---

## Saídas Geradas

### Parte 1

| Arquivo | Descrição |
|---------|-----------|
| `out/global.json` | Ordem, tamanho e densidade do grafo completo |
| `out/regioes.json` | Métricas de cada subgrafo regional |
| `out/ego_aeroportos.csv` | Grau, ordem, tamanho e densidade ego por aeroporto |
| `out/graus.csv` | Lista de graus por aeroporto |
| `out/rankings.json` | Aeroporto mais conectado e de maior densidade local |
| `out/distancias_rotas.csv` | Caminhos mínimos (Dijkstra) para 7 pares |
| `out/arvore_percurso.html` | Visualização interativa dos caminhos REC→POA e MAO→GRU |
| `out/grafo_interativo.html` | Grafo pyvis com tooltip, busca e destaque de caminhos |

### Parte 2

| Arquivo | Descrição |
|---------|-----------|
| `out/parte2_report.json` | Benchmark completo: tempos, memória, complexidade |
| `out/bfs_dataset2.json`, `_f2.json`, `_f3.json` | BFS da Parte 2 para as 3 fontes padrão |
| `out/dfs_dataset2.json`, `_f2.json`, `_f3.json` | DFS da Parte 2 para as 3 fontes padrão |
| `out/dijkstra_dataset2_f*.json` | Dijkstra da Parte 2 para 5 pares entre fontes |
| `out/bellman_ford_dataset2_f*.json` | Bellman-Ford da Parte 2 para 3 pares entre fontes |
| `out/bellman_ford_peso_negativo.json` | Caso sintético: peso negativo sem ciclo negativo |
| `out/bellman_ford_ciclo_negativo.json` | Caso sintético: ciclo negativo detectado |

### Visualizações

| Arquivo | Tipo | Insight |
|---------|------|---------|
| `viz1_distribuicao_graus.png` | Histograma | Distribuição de graus da rede Spotify — concentração entre 7 e 12 |
| `viz2_ranking_aeroportos.png` | Barras ordenadas | BSB e GRU são os hubs nacionais dominantes |
| `viz3_comparacao_regioes.png` | Barras agrupadas | Nordeste tem mais aeroportos mas menor densidade |
| `viz4_bfs_camadas_BSB.png` | Camadas BFS | BSB alcança todos em até 3 saltos — centralidade hub |
| `viz10_1_heatmap_adjacencias.png` | Heatmap | Concentração de conexões entre regiões Sul/Sudeste |
| `viz10_2_centralidade_grau.png` | Rede colorida | Centralidade de grau evidencia BSB como hub principal |
| `viz10_3_vulnerabilidade_barras.png` | Barras agrupadas | Perfil multidimensional de centralidade e ego-rede dos hubs principais |
| `viz10_4_mapa_conectividade.png` | Mapa geográfico | Distribuição espacial das rotas pelo território |

---

## Resultados de Benchmark

Executado no grafo Spotify (4.000 vértices, 19.717 arestas), média de 5 execuções:

| Algoritmo | Tempo médio | Memória pico | Complexidade |
|-----------|-------------|--------------|--------------|
| BFS | 18,43 ms | 797 KB | O(V + E) |
| Componentes Conexas (DFS) | 27,50 ms | 245 KB | O(V + E) |
| Dijkstra | 49,90 ms | 684 KB | O((V+E) log V) |
| DFS | 428,01 ms | 13.406 KB | O(V + E) |
| Bellman-Ford | 1.895,43 ms | 5.226 KB | O(V × E) |

**Razões:**
- Bellman-Ford é **38×** mais lento que Dijkstra
- Bellman-Ford é **102,9×** mais lento que BFS

**Conclusões:** Para grafos com pesos não-negativos, Dijkstra é sempre preferível ao Bellman-Ford. Bellman-Ford se torna indispensável apenas quando há pesos negativos ou quando é necessário detectar ciclos negativos — ambos os casos foram demonstrados nos arquivos `out/bellman_ford_peso_negativo.json` e `out/bellman_ford_ciclo_negativo.json`.

---

## Dependências

```
matplotlib>=3.10
numpy>=2.0
geopandas>=1.0
pyvis>=0.3
pytest>=7.0
```

> Os algoritmos BFS, DFS, Dijkstra e Bellman-Ford foram **implementados do zero** em `src/graphs/algorithms.py`, sem uso de NetworkX, igraph ou similares. O módulo `heapq` da biblioteca padrão do Python é utilizado internamente pelo Dijkstra.
